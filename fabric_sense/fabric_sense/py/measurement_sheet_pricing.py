# Copyright (c) 2025, innogenio and contributors
# For license information, please see license.txt

import frappe  # type: ignore
from typing import Dict, List, Any, Optional
from erpnext.stock.get_item_details import get_item_details


# Constants
SELECTION_ITEM_QTY = 1
VALID_MARGIN_TYPES = ["Percentage", "Amount"]


def _get_price_list_from_customer(customer: str) -> Optional[str]:
    """
    Get price list from customer by following the chain:
    Customer → customer_group → default_price_list

    Args:
            customer: Customer name

    Returns:
            Price list name or None if not found
    """
    if not customer:
        return None

    try:
        # Get customer_group from Customer
        customer_group = frappe.db.get_value("Customer", customer, "customer_group")
        if not customer_group:
            return None

        # Get default_price_list from Customer Group
        default_price_list = frappe.db.get_value(
            "Customer Group", customer_group, "default_price_list"
        )
        return default_price_list
    except Exception as e:
        frappe.log_error(
            f"Error getting price list from customer {customer}: {str(e)}\n{frappe.get_traceback()}",
            "Get Price List Error",
        )
        return None


def _get_default_selling_price_list() -> Optional[str]:
    """
    Get default selling price list from Selling Settings.

    Returns:
            Default selling price list name or None if not found
    """
    try:
        default_price_list = frappe.db.get_value(
            "Selling Settings", "Selling Settings", "selling_price_list"
        )
        return default_price_list
    except Exception as e:
        frappe.log_error(
            f"Error getting default selling price list: {str(e)}\n{frappe.get_traceback()}",
            "Get Default Price List Error",
        )
        return None


def _get_selection_item_rates(
    selection_items: List[str], price_list: Optional[str] = None
) -> Dict[str, float]:
    """
    Get rates for selection items (Blinds) from Item Price.
    Uses batch queries to avoid N+1 query problem.
    
    Price lookup order:
    1. Customer's price list (if provided)
    2. Default Selling Price List (from Selling Settings)
    3. If not found: 0.0

    Args:
            selection_items: List of item codes
            price_list: Optional price list name to filter by

    Returns:
            Mapping of item_code to rate (defaults to 0 if not found in price lists)
    """
    if not selection_items:
        return {}

    # Remove duplicates to avoid unnecessary queries
    unique_items = list(set(selection_items))

    # First, try to get prices from the specific price_list (if provided)
    item_prices = {}
    if price_list:
        filters = {
            "item_code": ["in", unique_items],
            "selling": 1,
            "price_list": price_list,
        }
        price_list_data = frappe.db.get_all(
            "Item Price",
            filters=filters,
            fields=["item_code", "price_list_rate"],
            order_by="modified desc",
        )

        # Group by item_code and get the most recent price for each
        seen_items = set()
        for price in price_list_data:
            if price.item_code not in seen_items and price.price_list_rate is not None:
                item_prices[price.item_code] = float(price.price_list_rate)
                seen_items.add(price.item_code)

    # Fallback: Try to get prices from default selling price list (if items still missing)
    items_without_prices = [item for item in unique_items if item not in item_prices]
    if items_without_prices:
        default_price_list = _get_default_selling_price_list()
        if default_price_list and default_price_list != price_list:
            filters = {
                "item_code": ["in", items_without_prices],
                "selling": 1,
                "price_list": default_price_list,
            }
            default_price_data = frappe.db.get_all(
                "Item Price",
                filters=filters,
                fields=["item_code", "price_list_rate"],
                order_by="modified desc",
            )

            seen_items = set(item_prices.keys())
            for price in default_price_data:
                if (
                    price.item_code not in seen_items
                    and price.price_list_rate is not None
                ):
                    item_prices[price.item_code] = float(price.price_list_rate)
                    seen_items.add(price.item_code)

    # Ensure all items have a rate (default to 0 if not found in any price list)
    result = {}
    for item in unique_items:
        result[item] = item_prices.get(item, 0.0)

    return result


@frappe.whitelist()
def get_fresh_item_price(item_code, customer=None):
    """
    Fetch item price using ERPNext pricing engine
    (same logic as Sales Order).

    Price list selection:
    1. If customer has a customer_group with a default_price_list, use that price list.
    2. Otherwise, fall back to the system's Standard Selling price list.
    """

    if not item_code:
        return {"price_list_rate": 0}

    company = frappe.defaults.get_user_default("Company")

    # Derive price list from customer's customer group, if any
    price_list = None
    if customer:
        price_list = _get_price_list_from_customer(customer)

    if not price_list:
        # Fallback: Standard Selling
        price_list = "Standard Selling"

    args = {
        "doctype": "Sales Order",  # IMPORTANT
        "item_code": item_code,
        "qty": 1,
        "price_list": price_list,
        "customer": customer,
        "company": company,
        "transaction_type": "selling",
        "conversion_rate": 1,
        "price_list_currency": "INR",
        "plc_conversion_rate": 1,
    }

    item_details = get_item_details(args)

    return {
        "price_list_rate": item_details.get("price_list_rate") or 0,
        "pricing_rule": item_details.get("pricing_rule"),
        "discount_percentage": item_details.get("discount_percentage"),
    }


def _is_service_item(item_code: str) -> bool:
    """
    Check if an item is a service item (stitching or fitting) that should be excluded from pricing rules.
    
    Args:
        item_code: Item code to check
    
    Returns:
        True if item is a service item, False otherwise
    """
    if not item_code:
        return False
    
    try:
        item_group = frappe.db.get_value("Item", item_code, "item_group")
        if not item_group:
            return False
        
        # Check if item_group is "Stitching" or "Labour" (root level)
        if item_group in ["Stitching", "Labour"]:
            return True
        
        # Check if item_group starts with "Stitching/" or "Labour/" (child groups)
        if item_group.startswith("Stitching/") or item_group.startswith("Labour/"):
            return True
        
        # Check parent_item_group if item_group is a child
        if frappe.db.exists("Item Group", item_group):
            item_group_doc = frappe.get_doc("Item Group", item_group)
            if (
                hasattr(item_group_doc, "parent_item_group")
                and item_group_doc.parent_item_group
            ):
                parent_group = item_group_doc.parent_item_group
                if parent_group in ["Stitching", "Labour"]:
                    return True
        
        return False
    except Exception:
        return False


def get_consolidated_items_with_pricing_rules(
    measurement_details: List,
    customer: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Extract and consolidate material items from measurement_details, then apply pricing rules.
    Excludes service items (stitching and fitting).
    
    Args:
        measurement_details: List of Measurement Detail rows
        customer: Customer name for price list and pricing rule context
    
    Returns:
        List of consolidated items with pricing details
    """
    try:
        # Dictionary to consolidate items by item_code
        consolidated_items = {}
        
        # Extract material items from measurement_details
        for md_row in measurement_details:
            # Fabric
            if md_row.fabric_selected and not _is_service_item(md_row.fabric_selected):
                item_code = md_row.fabric_selected
                qty = float(md_row.fabric_qty or 0)
                if qty > 0:
                    if item_code in consolidated_items:
                        consolidated_items[item_code]["qty"] += qty
                    else:
                        consolidated_items[item_code] = {
                            "item_code": item_code,
                            "qty": qty,
                            "source": "fabric_selected",
                        }
            
            # Lining
            if md_row.lining and not _is_service_item(md_row.lining):
                item_code = md_row.lining
                qty = float(md_row.lining_qty or 0)
                if qty > 0:
                    if item_code in consolidated_items:
                        consolidated_items[item_code]["qty"] += qty
                    else:
                        consolidated_items[item_code] = {
                            "item_code": item_code,
                            "qty": qty,
                            "source": "lining",
                        }
            
            # Lead Rope
            if md_row.lead_rope and not _is_service_item(md_row.lead_rope):
                item_code = md_row.lead_rope
                qty = float(md_row.lead_rope_qty or 0)
                if qty > 0:
                    if item_code in consolidated_items:
                        consolidated_items[item_code]["qty"] += qty
                    else:
                        consolidated_items[item_code] = {
                            "item_code": item_code,
                            "qty": qty,
                            "source": "lead_rope",
                        }
            
            # Track/Rod (Hardware)
            if md_row.track_rod and not _is_service_item(md_row.track_rod):
                item_code = md_row.track_rod
                qty = float(md_row.track_rod_qty or 0)
                if qty > 0:
                    if item_code in consolidated_items:
                        consolidated_items[item_code]["qty"] += qty
                    else:
                        consolidated_items[item_code] = {
                            "item_code": item_code,
                            "qty": qty,
                            "source": "track_rod",
                        }
            
            # Selection (for Blinds - hardware item)
            if md_row.selection and not _is_service_item(md_row.selection):
                item_code = md_row.selection
                # For Blinds: use square_feet as quantity
                if md_row.product_type == "Blinds" and md_row.square_feet:
                    qty = float(md_row.square_feet or 0)
                else:
                    qty = SELECTION_ITEM_QTY
                if qty > 0:
                    if item_code in consolidated_items:
                        consolidated_items[item_code]["qty"] += qty
                    else:
                        consolidated_items[item_code] = {
                            "item_code": item_code,
                            "qty": qty,
                            "source": "selection",
                        }
        
        # Convert to list
        result = []
        for item_code, item_data in consolidated_items.items():
            result.append(item_data)
        
        return result
        
    except Exception as e:
        frappe.log_error(
            f"Error in get_consolidated_items_with_pricing_rules: {str(e)}\n{frappe.get_traceback()}",
            "Get Consolidated Items Error",
        )
        return []


def apply_pricing_rule_to_item(
    item_code: str,
    quantity: float,
    customer: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Apply pricing rule to an item and calculate discount and final price.
    Uses price from customer's price list (if exists) instead of standard selling price.
    
    Args:
        item_code: Item code
        quantity: Consolidated quantity
        customer: Optional customer name
    
    Returns:
        Dict with pricing details: base_price, discount_amount, final_price, pricing_rule_name
    """
    try:
        if not item_code or quantity <= 0:
            return {
                "base_price": 0,
                "discount_amount": 0,
                "final_price": 0,
                "pricing_rule_name": None,
            }
        
        # Get customer's price list
        price_list = None
        if customer:
            price_list = _get_price_list_from_customer(customer)
        
        # Get base price from price list (if exists) or standard selling price
        price_data = get_fresh_item_price(item_code, customer)
        base_price = float(price_data.get("price_list_rate", 0) or 0)
        
        if base_price <= 0:
            return {
                "base_price": 0,
                "discount_amount": 0,
                "final_price": 0,
                "pricing_rule_name": None,
            }
        
        # Get item_group for the item
        item_group = frappe.db.get_value("Item", item_code, "item_group")
        
        # Get applicable pricing rule
        pricing_rule = _get_applicable_pricing_rules(
            item_code=item_code,
            item_group=item_group or "",
            quantity=quantity,
            customer=customer,
            price_list=price_list,
        )
        
        if not pricing_rule:
            # No pricing rule applies
            return {
                "base_price": base_price,
                "discount_amount": 0,
                "final_price": base_price,
                "pricing_rule_name": None,
            }
        
        # Check price_or_product_discount field to determine if it's a Price rule or Discount rule
        price_or_product_discount = pricing_rule.get("price_or_product_discount")
        
        # Check if pricing rule has a fixed rate (overrides base price)
        rule_rate = pricing_rule.get("rate")
        rule_rate_float = float(rule_rate or 0) if rule_rate is not None else 0.0
        
        if price_or_product_discount == "Price" and rule_rate_float > 0:
            # Use the rate from pricing rule directly (Price type rule with fixed rate)
            final_price = rule_rate_float
            discount_amount = base_price - final_price
        else:
            # Check if pricing rule has margin (margin increases price)
            margin_type = pricing_rule.get("margin_type")
            margin_rate_or_amount_raw = pricing_rule.get("margin_rate_or_amount")
            
            # Convert margin_rate_or_amount to float, handling None, empty strings, and Decimal types
            try:
                if margin_rate_or_amount_raw is None or margin_rate_or_amount_raw == "":
                    margin_rate_or_amount = 0.0
                else:
                    margin_rate_or_amount = float(margin_rate_or_amount_raw)
            except (ValueError, TypeError):
                margin_rate_or_amount = 0.0
            
            # Apply margin if margin_type and margin_rate_or_amount are valid
            # Check absolute value to handle both positive and negative margins
            margin_applied = False
            if margin_type and margin_rate_or_amount is not None and abs(margin_rate_or_amount) > 0.0001:
                # Validate margin_type against ERPNext's allowed values
                if margin_type not in VALID_MARGIN_TYPES:
                    # Invalid margin_type - log warning and fall through to discount logic
                    frappe.log_error(
                        f"Invalid margin_type '{margin_type}' in pricing rule {pricing_rule.get('name')}. "
                        f"Valid types are: {', '.join(VALID_MARGIN_TYPES)}. Falling back to discount logic.",
                        "Pricing Rule Invalid Margin Type"
                    )
                    margin_applied = False
                elif margin_type == "Percentage":
                    # Percentage margin: final_price = base_price * (1 + margin_rate_or_amount / 100)
                    # Negative margin reduces price, positive margin increases price
                    final_price = base_price * (1 + margin_rate_or_amount / 100.0)
                    discount_amount = base_price - final_price  # Negative if margin increases price, positive if margin decreases price
                    margin_applied = True
                elif margin_type == "Amount":
                    # Amount margin: final_price = base_price + margin_rate_or_amount
                    # Negative margin reduces price, positive margin increases price
                    final_price = base_price + margin_rate_or_amount
                    discount_amount = base_price - final_price  # Negative if margin increases price, positive if margin decreases price
                    margin_applied = True
            
            # If margin was not applied, check for discount
            if not margin_applied:
                # Handle Discount type OR Price type with no fixed rate (use discount_percentage/discount_amount)
                # Calculate discount based on pricing rule
                # Check if it's percentage or amount discount
                discount_percentage_raw = pricing_rule.get("discount_percentage")
                discount_amount_raw = pricing_rule.get("discount_amount")
                
                # Handle NULL, empty string, or Decimal types from SQL
                # Convert to float, handling None, empty strings, and Decimal types
                try:
                    if discount_percentage_raw is None or discount_percentage_raw == "":
                        discount_percentage = 0.0
                    else:
                        # Handle Decimal type from MySQL
                        discount_percentage = float(discount_percentage_raw)
                except (ValueError, TypeError):
                    discount_percentage = 0.0
                
                try:
                    if discount_amount_raw is None or discount_amount_raw == "":
                        discount_amount_field = 0.0
                    else:
                        # Handle Decimal type from MySQL
                        discount_amount_field = float(discount_amount_raw)
                except (ValueError, TypeError):
                    discount_amount_field = 0.0
                
                # Check if discount_percentage is greater than 0 (with small epsilon to handle floating point)
                if discount_percentage and discount_percentage > 0.0001:
                    # Percentage discount
                    discount_amount = (base_price * discount_percentage) / 100.0
                elif discount_amount_field and discount_amount_field > 0.0001:
                    # Amount discount
                    discount_amount = discount_amount_field
                else:
                    # No discount specified
                    discount_amount = 0
                
                # Calculate final price
                final_price = base_price - discount_amount
                if final_price < 0:
                    final_price = 0
        
        return {
            "base_price": base_price,
            "discount_amount": discount_amount,
            "final_price": final_price,
            "pricing_rule_name": pricing_rule.get("name"),
        }
        
    except Exception as e:
        frappe.log_error(
            f"Error in apply_pricing_rule_to_item for {item_code}: {str(e)}\n{frappe.get_traceback()}",
            "Apply Pricing Rule Error",
        )
        return {
            "base_price": 0,
            "discount_amount": 0,
            "final_price": 0,
            "pricing_rule_name": None,
        }


def _get_applicable_pricing_rules(
    item_code: str,
    item_group: str,
    quantity: float,
    customer: Optional[str] = None,
    price_list: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get applicable pricing rule for an item based on item_code, item_group, quantity, customer, and price_list.
    
    Args:
        item_code: Item code
        item_group: Item group of the item
        quantity: Consolidated quantity
        customer: Optional customer name
        price_list: Optional price list name (from customer_group)
    
    Returns:
        Best matching pricing rule dict or None if no rule found
    """
    try:
        if not item_code or quantity <= 0:
            return None

        # Derive customer_group for additional rule filtering
        customer_group = None
        if customer:
            customer_group = frappe.db.get_value("Customer", customer, "customer_group")

        # Build filters for pricing rule query (kept for reference; actual filtering
        # is done via explicit SQL conditions below)
        filters = [
            ["disable", "=", 0],
            ["selling", "=", 1],
            ["min_qty", "<=", quantity],
        ]

        # Try item_code first (more specific)
        # Use SQL with JOIN to child table for item_code filtering
        conditions = [
            "pr.disable = 0",
            "pr.selling = 1",
            f"pr.min_qty <= {float(quantity)}",
            f"(pr.max_qty IS NULL OR pr.max_qty = 0 OR pr.max_qty >= {float(quantity)})",
            "pr.apply_on = 'Item Code'",
            f"pr_item.item_code = {frappe.db.escape(item_code)}",
        ]

        # Handle customer filter:
        # rule applies if customer IS NULL/'' OR matches the specific customer
        if customer:
            conditions.append(
                f"(pr.customer IS NULL OR pr.customer = '' OR pr.customer = {frappe.db.escape(customer)})"
            )
        else:
            conditions.append("(pr.customer IS NULL OR pr.customer = '')")

        # Handle customer_group filter:
        # rule applies if customer_group IS NULL/'' OR matches the customer's group
        if customer_group:
            conditions.append(
                f"(pr.customer_group IS NULL OR pr.customer_group = '' OR pr.customer_group = {frappe.db.escape(customer_group)})"
            )
        else:
            conditions.append("(pr.customer_group IS NULL OR pr.customer_group = '')")

        # Handle price_list filter:
        # rule applies if for_price_list IS NULL/'' OR matches the specific price_list
        if price_list:
            conditions.append(
                f"(pr.for_price_list IS NULL OR pr.for_price_list = '' OR pr.for_price_list = {frappe.db.escape(price_list)})"
            )
        else:
            conditions.append("(pr.for_price_list IS NULL OR pr.for_price_list = '')")
        
        sql = f"""
            SELECT DISTINCT pr.name, pr.priority, pr.min_qty, pr.max_qty, pr.discount_percentage, 
                   pr.discount_amount, pr.rate, pr.customer, pr.for_price_list, 
                   pr.price_or_product_discount, pr.margin_type, pr.margin_rate_or_amount
            FROM `tabPricing Rule` pr
            INNER JOIN `tabPricing Rule Item Code` pr_item 
                ON pr.name = pr_item.parent
            WHERE {' AND '.join(conditions)}
            ORDER BY pr.priority DESC, pr.min_qty DESC
            LIMIT 10
        """
        
        item_code_rules = frappe.db.sql(sql, as_dict=True)
        
        if item_code_rules:
            return item_code_rules[0]  # Return the best match
        
        # If no item_code rule, try item_group (less specific)
        if item_group:
            conditions = [
                "pr.disable = 0",
                "pr.selling = 1",
                f"pr.min_qty <= {float(quantity)}",
                f"(pr.max_qty IS NULL OR pr.max_qty = 0 OR pr.max_qty >= {float(quantity)})",
                "pr.apply_on = 'Item Group'",
                f"pr_group.item_group = {frappe.db.escape(item_group)}",
            ]

            # Handle customer filter
            if customer:
                conditions.append(
                    f"(pr.customer IS NULL OR pr.customer = '' OR pr.customer = {frappe.db.escape(customer)})"
                )
            else:
                conditions.append("(pr.customer IS NULL OR pr.customer = '')")

            # Handle customer_group filter
            if customer_group:
                conditions.append(
                    f"(pr.customer_group IS NULL OR pr.customer_group = '' OR pr.customer_group = {frappe.db.escape(customer_group)})"
                )
            else:
                conditions.append("(pr.customer_group IS NULL OR pr.customer_group = '')")

            # Handle price_list filter
            if price_list:
                conditions.append(
                    f"(pr.for_price_list IS NULL OR pr.for_price_list = '' OR pr.for_price_list = {frappe.db.escape(price_list)})"
                )
            else:
                conditions.append("(pr.for_price_list IS NULL OR pr.for_price_list = '')")
            
            sql = f"""
                SELECT DISTINCT pr.name, pr.priority, pr.min_qty, pr.max_qty, pr.discount_percentage, 
                       pr.discount_amount, pr.rate, pr.customer, pr.for_price_list, 
                       pr.price_or_product_discount, pr.margin_type, pr.margin_rate_or_amount
                FROM `tabPricing Rule` pr
                INNER JOIN `tabPricing Rule Item Group` pr_group 
                    ON pr.name = pr_group.parent
                WHERE {' AND '.join(conditions)}
                ORDER BY pr.priority DESC, pr.min_qty DESC
                LIMIT 10
            """
            
            item_group_rules = frappe.db.sql(sql, as_dict=True)
            
            if item_group_rules:
                return item_group_rules[0]  # Return the best match
        
        return None
        
    except Exception as e:
        frappe.log_error(
            f"Error in _get_applicable_pricing_rules for {item_code}: {str(e)}\n{frappe.get_traceback()}",
            "Get Applicable Pricing Rules Error",
        )
        return None


@frappe.whitelist()
def get_pricing_summary(measurement_sheet_name: str) -> Dict[str, Any]:
    """
    Get pricing summary with consolidated items and applied pricing rules.
    
    Args:
        measurement_sheet_name: Name of the Measurement Sheet
    
    Returns:
        Dict with pricing summary data for frontend table
    """
    try:
        # Get the Measurement Sheet document
        ms = frappe.get_doc("Measurement Sheet", measurement_sheet_name)
        
        if not ms.customer:
            return {
                "items": [],
                "error": "Customer is required to calculate pricing summary",
            }
        
        if not ms.measurement_details or len(ms.measurement_details) == 0:
            return {
                "items": [],
                "error": None,
            }
        
        # Get consolidated items
        consolidated_items = get_consolidated_items_with_pricing_rules(
            ms.measurement_details,
            ms.customer,
        )
        
        if not consolidated_items:
            return {
                "items": [],
                "error": None,
            }
        
        # Apply pricing rules to each consolidated item
        pricing_summary = []
        for item_data in consolidated_items:
            item_code = item_data["item_code"]
            quantity = item_data["qty"]
            
            # Get item name
            item_name = frappe.db.get_value("Item", item_code, "item_name") or item_code
            
            # Apply pricing rule
            pricing_data = apply_pricing_rule_to_item(
                item_code=item_code,
                quantity=quantity,
                customer=ms.customer,
            )
            
            # Get item_group for the item
            item_group = frappe.db.get_value("Item", item_code, "item_group") or ""
            
            pricing_summary.append({
                "item_code": item_code,
                "item_name": item_name,
                "item_group": item_group,
                "quantity": quantity,
                "actual_price": pricing_data["base_price"],
                "discount": pricing_data["discount_amount"],
                "price_after_discount": pricing_data["final_price"],
                "pricing_rule": pricing_data["pricing_rule_name"] or "-",
            })
        
        return {
            "items": pricing_summary,
            "error": None,
        }
        
    except Exception as e:
        frappe.log_error(
            f"Error in get_pricing_summary for {measurement_sheet_name}: {str(e)}\n{frappe.get_traceback()}",
            "Get Pricing Summary Error",
        )
        return {
            "items": [],
            "error": f"Error calculating pricing summary: {str(e)}",
        }

