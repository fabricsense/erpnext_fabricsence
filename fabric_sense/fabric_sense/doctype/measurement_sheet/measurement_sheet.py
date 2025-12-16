# Copyright (c) 2025, innogenio and contributors
# For license information, please see license.txt

import frappe  # type: ignore
from frappe.model.document import Document  # type: ignore
from frappe.utils import formatdate  # type: ignore
from typing import Dict, List, Any, Optional
import erpnext  # type: ignore

# Constants
STATUS_APPROVED = "Approved"
SERVICE_CHARGE_QTY = 1
SELECTION_ITEM_QTY = 1


class MeasurementSheet(Document):
    """
    Main doctype for capturing customer window furnishing measurements.
    Includes basic information, contractor assignment, measurement details, and summary calculations.
    """

    def before_insert(self):
        """Set default values before inserting a new document"""
        # Auto-fill sales_person with logged-in user's full name if not set
        if not self.sales_person:
            user_full_name = frappe.utils.get_fullname(frappe.session.user)
            if user_full_name:
                self.sales_person = user_full_name

    def validate(self):
        """Validate document before saving"""
        self.validate_customer()
        self.validate_contractor_assignment()
        self.validate_measurement_details()
        self.validate_project_uniqueness()
        # Calculate totals during validation to sync with client-side
        self.calculate_totals()

    def validate_customer(self):
        """Validate customer field is present and exists"""
        # Check if customer is empty, None, or whitespace
        if not self.customer or (
            isinstance(self.customer, str) and not self.customer.strip()
        ):
            frappe.throw(
                "Customer is mandatory for Measurement Sheet", frappe.MandatoryError
            )

        # Validate customer exists in database
        if not frappe.db.exists("Customer", self.customer):
            frappe.throw(f"Customer '{self.customer}' does not exist in the system")

    def validate_contractor_assignment(self):
        """Validate contractor assignment fields when measurement method is 'Contractor Assigned'"""
        if self.measurement_method == "Contractor Assigned":
            if not self.assigned_contractor:
                frappe.throw(
                    "Assigned Contractor is mandatory when Measurement Method is 'Contractor Assigned'"
                )

            if not self.expected_measurement_date:
                frappe.throw(
                    "Expected Measurement Date is mandatory when Measurement Method is 'Contractor Assigned'"
                )

            if self.site_visit_required and not self.visiting_charge:
                frappe.throw(
                    "Visiting Charge is mandatory when Site Visit Required is checked"
                )

    def validate_measurement_details(self):
        """Validate that measurement details table has at least one row"""
        if not self.measurement_details or len(self.measurement_details) == 0:
            frappe.throw("At least one Measurement Detail is required")

        # Validate each measurement detail row
        for row in self.measurement_details:
            self.validate_measurement_detail_row(row)

    def validate_project_uniqueness(self):
        """Ensure only one Measurement Sheet per Project"""
        if self.project:
            # Check for existing Measurement Sheet with same project
            existing = frappe.db.exists(
                "Measurement Sheet",
                {
                    "project": self.project,
                    "name": ["!=", self.name],  # Exclude current document
                    "docstatus": ["!=", 2]  # Exclude cancelled documents
                }
            )
            if existing:
                frappe.throw(
                    f"Measurement Sheet '{existing}' already exists for Project '{self.project}'. "
                    "Only one Measurement Sheet is allowed per Project.",
                    title="Duplicate Project"
                )

    def validate_measurement_detail_row(self, row):
        """Validate individual measurement detail row based on product type"""
        if not row.product_type:
            frappe.throw("Product Type is required for all measurement details")

        if not row.area:
            frappe.throw("Area is required for all measurement details")

        if not row.width:
            frappe.throw("Width is required for all measurement details")

        # Height is required for all except Tracks/Rods
        if row.product_type != "Tracks/Rods" and not row.height:
            frappe.throw(f"Height is required for Product Type: {row.product_type}")

        # Validate panels field: must be > 0 for Window Curtains and Roman Blinds
        if row.product_type in ["Window Curtains", "Roman Blinds"]:
            if not row.panels or int(row.panels) <= 0:
                frappe.throw(
                    f"Panel must be greater than 0 for {row.product_type}. Please enter a valid quantity.",
                    title="Invalid Panel Value",
                )

        # Validate product type specific requirements
        if row.product_type == "Window Curtains":
            if not row.fabric_selected:
                frappe.throw("Fabric Selected is required for Window Curtains")

        elif row.product_type == "Roman Blinds":
            if not row.fabric_selected:
                frappe.throw("Fabric Selected is required for Roman Blinds")

        elif row.product_type == "Blinds":
            if not row.selection:
                frappe.throw("Selection is required for Blinds")

    def calculate_totals(self):
        """Calculate total amount including visiting charge"""
        total_amount = 0

        # Sum all amounts from measurement details
        if self.measurement_details:
            for row in self.measurement_details:
                if row.amount:
                    total_amount += row.amount

        # Add visiting charge if present
        visiting_charge = float(self.visiting_charge or 0)
        self.total_amount = total_amount + visiting_charge

    def on_update(self):
        """Called when document is updated"""
        # Auto-update actual_measurement_date if measurement_method is Contractor Assigned
        if (
            self.measurement_method == "Contractor Assigned"
            and not self.actual_measurement_date
        ):
            # This can be set manually or via workflow
            pass

    def before_save(self):
        """Called before saving the document"""
        # Totals are already calculated in validate(), no need to recalculate here
        # The validate() method ensures totals are always up-to-date
        # Notify tailor (assigned contractor) when assignment changes
        try:
            if (
                self.assigned_contractor
                and not self.is_new()
                and self.has_value_changed("assigned_contractor")
                and not getattr(self.flags, "_contractor_notified", False)
            ):
                self.notify_assigned_contractor()
        except Exception:
            # Do not block save due to notification errors
            frappe.log_error(
                frappe.get_traceback(),
                "Measurement Sheet: Notification Error in before_save",
            )

    def after_insert(self):
        """Called right after document is inserted (for new docs)"""
        try:
            if self.assigned_contractor:
                self.notify_assigned_contractor()
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                "Measurement Sheet: Notification Error in after_insert",
            )

    def notify_assigned_contractor(self):
        """Send an email to the assigned contractor (tailor) informing assignment."""
        recipient = self._get_contractor_email(self.assigned_contractor)
        if not recipient:
            return

        # Get contractor name for personalization
        contractor_name = (
            frappe.db.get_value("Employee", self.assigned_contractor, "employee_name")
            or "there"
        )

        # Build subject with emoji for visual appeal
        subject = f"New Measurement Assignment - {self.name or ''}"

        # Prepare data rows
        rows = []

        # Measurement ID
        rows.append(
            f"""
			<tr>
				<td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
					<strong style="color: #374151;">Measurement ID</strong>
				</td>
				<td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
					<span style="font-family: 'Courier New', monospace; color: #1f2937; font-weight: 600;">{frappe.utils.escape_html(self.name or '')}</span>
				</td>
			</tr>
		"""
        )

        # Customer
        if self.customer:
            customer_name = (
                frappe.db.get_value("Customer", self.customer, "customer_name")
                or self.customer
            )
            rows.append(
                f"""
				<tr>
					<td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
						<strong style="color: #374151;">Customer</strong>
					</td>
					<td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
						<span style="color: #1f2937;">{frappe.utils.escape_html(customer_name)}</span>
					</td>
				</tr>
			"""
            )

        # Expected Measurement Date
        if self.expected_measurement_date:
            rows.append(
                f"""
				<tr>
					<td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
						<strong style="color: #374151;">📅 Expected Date</strong>
					</td>
					<td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
						<span style="color: #1f2937; font-weight: 600;">{formatdate(self.expected_measurement_date)}</span>
					</td>
				</tr>
			"""
            )

        # Actual Measurement Date
        if getattr(self, "actual_measurement_date", None):
            rows.append(
                f"""
				<tr>
					<td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
						<strong style="color: #374151;">Actual Date</strong>
					</td>
					<td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
						<span style="color: #1f2937;">{formatdate(self.actual_measurement_date)}</span>
					</td>
				</tr>
			"""
            )

        # Visiting Charge
        if getattr(self, "visiting_charge", None):
            rows.append(
                f"""
				<tr>
					<td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
						<strong style="color: #374151;">💰 Visiting Charge</strong>
					</td>
					<td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
						<span style="color: #059669; font-weight: 600; font-size: 15px;">{frappe.format_value(self.visiting_charge, {'fieldtype': 'Currency'})}</span>
					</td>
				</tr>
			"""
            )

        rows_html = "".join(rows)

        # Build special instructions section
        special_instructions_html = ""
        if getattr(self, "special_instructions", None):
            special_instructions_html = f"""
				<div style="padding: 0 24px 24px;">
					<div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 6px;">
						<p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.6;">
							<strong>⚠️ Note:</strong> {frappe.utils.escape_html(self.special_instructions)}
						</p>
					</div>
				</div>
			"""

        # Build the complete HTML message with modern styling
        message = f"""
			<!DOCTYPE html>
			<html>
			<head>
				<meta charset="UTF-8">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
			</head>
			<body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', 'Roboto', 'Helvetica Neue', Arial, sans-serif;">
				<div style="max-width: 600px; margin: 0 auto; padding: 20px;">
					<!-- Header Card -->
					<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px 12px 0 0; padding: 32px 24px; text-align: center;">
						<div style="background-color: white; width: 60px; height: 60px; border-radius: 50%; margin: 0 auto 12px; padding-top: 8px;">
							<span style="font-size: 28px;">📏</span>
						</div>
						<h1 style="margin: 0; color: white; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;">New Measurement Assignment</h1>
						<p style="margin: 8px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">You have been assigned to collect measurements</p>
					</div>
					
					<!-- Main Content Card -->
					<div style="background-color: white; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
						<!-- Greeting -->
						<div style="padding: 24px 24px 16px;">
							<p style="margin: 0; font-size: 16px; color: #1f2937; line-height: 1.6;">
								Hello <strong style="color: #667eea;">{frappe.utils.escape_html(contractor_name)}</strong>,
							</p>
							<p style="margin: 12px 0 0; font-size: 15px; color: #4b5563; line-height: 1.6;">
								You have been assigned to a new measurement task. Please review the details below and proceed accordingly.
							</p>
						</div>
						
						<!-- Details Table -->
						<div style="padding: 0 24px 24px;">
							<table style="width: 100%; border-collapse: collapse; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
								<tbody>
									{rows_html}
								</tbody>
							</table>
						</div>						
						
						<!-- Special Instructions (if any) -->
						{special_instructions_html}
						
						
					</div>
					
					
				</div>
			</body>
			</html>
		"""

        frappe.sendmail(
            recipients=[recipient],
            subject=subject,
            message=message,
            reference_doctype=self.doctype,
            reference_name=self.name,
        )

    def _get_contractor_email(self, employee_id: str) -> str | None:
        """Resolve an email for the given Employee.
        Priority: linked User.email -> Employee.company_email -> Employee.personal_email -> Employee.prefered_email
        """
        if not employee_id:
            return None

        # Try linked User first
        user_id = frappe.db.get_value("Employee", employee_id, "user_id")
        if user_id:
            user_email = frappe.db.get_value("User", user_id, "email")
            if user_email:
                return user_email

        # Fallback to common email fields on Employee
        email_fields = [
            "company_email",
            "personal_email",
            "prefered_email",
            "prefered_contact_email",
        ]
        employee = frappe.db.get_value(
            "Employee", employee_id, email_fields, as_dict=True
        )
        if employee:
            for f in email_fields:
                eml = employee.get(f)
                if eml:
                    return eml

        return None


def _add_item_if_valid(
    items: List[Dict], item_code: Optional[str], qty: float, rate: float, item_idx: int
) -> int:
    """
    Add item to list if valid.

    Args:
            items: List to append to
            item_code: Item code (can be None/empty)
            qty: Quantity (must be > 0)
            rate: Rate
            item_idx: Current index

    Returns:
            Next item index
    """
    if item_code and qty and qty > 0:
        items.append(
            {"item_code": item_code, "qty": qty, "rate": rate or 0, "idx": item_idx}
        )
        return item_idx + 1
    return item_idx


def _add_service_charge_item_if_valid(
    items: List[Dict], item_code: Optional[str], charge: float, item_idx: int
) -> int:
    """
    Add service charge item to list if valid.

    Args:
            items: List to append to
            item_code: Item code (can be None/empty)
            charge: Charge amount (must be > 0)
            item_idx: Current index

    Returns:
            Next item index
    """
    if item_code and charge and charge > 0:
        items.append(
            {
                "item_code": item_code,
                "qty": SERVICE_CHARGE_QTY,
                "rate": charge,
                "idx": item_idx,
            }
        )
        return item_idx + 1
    return item_idx


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
    Get rates for selection items (Blinds) from Item Price or Item standard_rate.
    Uses batch queries to avoid N+1 query problem.

    Args:
            selection_items: List of item codes
            price_list: Optional price list name to filter by

    Returns:
            Mapping of item_code to rate (defaults to 0 if not found)
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

    # Final fallback: Get standard_rates for items still without prices
    items_without_prices = [item for item in unique_items if item not in item_prices]
    item_rates = {}
    if items_without_prices:
        items = frappe.db.get_all(
            "Item",
            filters={"name": ["in", items_without_prices]},
            fields=["name", "standard_rate"],
        )
        item_rates = {
            item.name: float(item.standard_rate or 0)
            for item in items
            if item.standard_rate is not None
        }

    # Ensure all items have a rate (default to 0)
    result = {}
    for item in unique_items:
        result[item] = item_prices.get(item, item_rates.get(item, 0.0))

    return result


def _extract_items_from_measurement_details(
    measurement_details: List, selection_rates: Optional[Dict[str, float]] = None
) -> List[Dict]:
    """
    Extract items from measurement details.

    Args:
            measurement_details: List of Measurement Detail rows
            selection_rates: Dict mapping item_code to rate for selection items

    Returns:
            List of item dictionaries
    """
    items = []
    item_idx = 1
    selection_rates = selection_rates or {}

    for md_row in measurement_details:
        # Add fabric_selected item
        item_idx = _add_item_if_valid(
            items,
            md_row.fabric_selected,
            md_row.fabric_qty,
            md_row.fabric_rate,
            item_idx,
        )

        # Add lining item
        item_idx = _add_item_if_valid(
            items, md_row.lining, md_row.lining_qty, md_row.lining_rate, item_idx
        )

        # Add lead_rope item
        item_idx = _add_item_if_valid(
            items,
            md_row.lead_rope,
            md_row.lead_rope_qty,
            md_row.lead_rope_rate,
            item_idx,
        )

        # Add track_rod item
        item_idx = _add_item_if_valid(
            items,
            md_row.track_rod,
            md_row.track_rod_qty,
            md_row.track_rod_rate,
            item_idx,
        )

        # Add selection item (for Blinds)
        if md_row.selection:
            selection_rate = selection_rates.get(md_row.selection, 0)
            # For Blinds: use square_feet as quantity
            if md_row.product_type == "Blinds" and md_row.square_feet:
                qty = md_row.square_feet
            else:
                qty = SELECTION_ITEM_QTY
            items.append(
                {
                    "item_code": md_row.selection,
                    "qty": qty,
                    "rate": selection_rate,
                    "idx": item_idx,
                }
            )
            item_idx += 1

        # Add stitching_pattern item
        # For Window Curtains: qty = panels, rate = stitching_charge / panels
        # For Roman Blinds: qty = sqft, rate = stitching_charge / sqft
        # For other types: qty = 1, rate = stitching_charge
        if (
            md_row.stitching_pattern
            and md_row.stitching_charge
            and md_row.stitching_charge > 0
        ):
            if (
                md_row.product_type == "Window Curtains"
                and md_row.panels
                and md_row.panels > 0
            ):
                # For Window Curtains: stitching_charge already contains (panels × rate)
                # So we divide by panels to get the per-panel rate
                stitching_rate_per_panel = md_row.stitching_charge / md_row.panels
                items.append(
                    {
                        "item_code": md_row.stitching_pattern,
                        "qty": md_row.panels,
                        "rate": stitching_rate_per_panel,
                        "idx": item_idx,
                    }
                )
                item_idx += 1
            elif (
                md_row.product_type == "Roman Blinds"
                and md_row.square_feet
                and md_row.square_feet > 0
            ):
                # For Roman Blinds: stitching_charge already contains (sqft × rate)
                # So we divide by sqft to get the per-sqft rate
                stitching_rate_per_sqft = md_row.stitching_charge / md_row.square_feet
                items.append(
                    {
                        "item_code": md_row.stitching_pattern,
                        "qty": md_row.square_feet,
                        "rate": stitching_rate_per_sqft,
                        "idx": item_idx,
                    }
                )
                item_idx += 1
            else:
                # For other product types: flat service charge
                items.append(
                    {
                        "item_code": md_row.stitching_pattern,
                        "qty": SERVICE_CHARGE_QTY,
                        "rate": md_row.stitching_charge,
                        "idx": item_idx,
                    }
                )
                item_idx += 1

        # Add fitting_type item
        item_idx = _add_service_charge_item_if_valid(
            items, md_row.fitting_type, md_row.fitting_charge, item_idx
        )

    # Group items by item_code and sum quantities
    grouped_items = {}
    for item in items:
        item_code = item["item_code"]
        if item_code in grouped_items:
            # Same item found - add quantities
            grouped_items[item_code]["qty"] += item["qty"]
        else:
            # New item - add to dictionary
            grouped_items[item_code] = item.copy()

    # Convert back to list with proper idx
    final_items = []
    for idx, item in enumerate(grouped_items.values(), 1):
        item["idx"] = idx
        final_items.append(item)

    return final_items


def _get_company_for_sales_order(customer: str) -> Optional[str]:
    """
    Get company for Sales Order.
    Priority: Customer's represents_company (for internal customers) -> System default company -> First available company

    Args:
            customer: Customer name

    Returns:
            Company name or None if not found
    """
    # Try to get customer's company (for internal customers)
    if customer:
        # Check if this is an internal customer with represents_company field
        is_internal_customer, represents_company = frappe.db.get_value(
            "Customer", customer, ["is_internal_customer", "represents_company"]
        ) or (None, None)

        if is_internal_customer and represents_company:
            return represents_company

    # Use ERPNext's default company function
    default_company = erpnext.get_default_company()
    if default_company:
        return default_company

    # Last resort: get any company from the system
    companies = frappe.get_all("Company", limit=1)
    if companies:
        return companies[0].name

    return None


@frappe.whitelist()
def get_sales_order_data_from_measurement_sheet(
    measurement_sheet_name: str,
) -> Dict[str, Any]:
    """
    Get Sales Order data from an approved Measurement Sheet for pre-populating a new Sales Order form.

    Args:
            measurement_sheet_name: Name of the Measurement Sheet

    Returns:
            Dictionary containing customer, project, measurement_sheet, company, and items data

    Raises:
            frappe.ValidationError: If Measurement Sheet is not approved or missing required data
            frappe.PermissionError: If user doesn't have read permission on Measurement Sheet
    """
    # Check permissions
    if not frappe.has_permission("Measurement Sheet", "read", measurement_sheet_name):
        frappe.log_error(
            f"Unauthorized access attempt to Measurement Sheet: {measurement_sheet_name} by user: {frappe.session.user}",
            "Sales Order Creation Permission Error",
        )
        frappe.throw(
            "Insufficient permissions to access Measurement Sheet",
            frappe.PermissionError,
        )

    # Get the Measurement Sheet document
    ms = frappe.get_doc("Measurement Sheet", measurement_sheet_name)

    # Validate Measurement Sheet is approved
    if ms.status != STATUS_APPROVED:
        frappe.log_error(
            f"Attempted to create Sales Order from non-approved Measurement Sheet: {measurement_sheet_name} (Status: {ms.status})",
            "Sales Order Creation Error",
        )
        frappe.throw(
            f"Measurement Sheet '{measurement_sheet_name}' must be '{STATUS_APPROVED}' to create Sales Order. Current status: {ms.status}"
        )

    # Validate customer exists
    if not ms.customer:
        frappe.log_error(
            f"Measurement Sheet '{measurement_sheet_name}' missing customer",
            "Sales Order Creation Error",
        )
        frappe.throw(
            f"Customer is required in Measurement Sheet '{measurement_sheet_name}' to create Sales Order"
        )

    # Validate measurement details exist
    if not ms.measurement_details or len(ms.measurement_details) == 0:
        frappe.log_error(
            f"Measurement Sheet '{measurement_sheet_name}' has no measurement details",
            "Sales Order Creation Error",
        )
        frappe.throw(
            f"Measurement Sheet '{measurement_sheet_name}' must have at least one Measurement Detail to create Sales Order"
        )

    # Get price list from customer's customer group
    price_list = _get_price_list_from_customer(ms.customer)
    # Get company - try customer's default company first, then system default
    company = _get_company_for_sales_order(ms.customer)
    if not company:
        frappe.throw(
            "Unable to determine Company for Sales Order. Please set a default company."
        )

    # Get selection item rates (batch query to avoid N+1)
    selection_items = [
        md_row.selection for md_row in ms.measurement_details if md_row.selection
    ]
    selection_rates = _get_selection_item_rates(selection_items, price_list)

    # Extract items
    items = _extract_items_from_measurement_details(
        ms.measurement_details, selection_rates
    )

    # Validate that at least one item was found
    if not items:
        frappe.log_error(
            f"No valid items found in Measurement Sheet '{measurement_sheet_name}'",
            "Sales Order Creation Error",
        )
        frappe.throw(
            f"No valid items found in Measurement Sheet '{measurement_sheet_name}' to create Sales Order"
        )

    # Return data for pre-populating Sales Order form
    return {
        "customer": ms.customer,
        "company": company,
        "transaction_date": frappe.utils.today(),
        "measurement_sheet": ms.name,
        "project": ms.project if ms.project else None,
        "items": items,
    }


def _get_all_item_groups_under_parent(parent_group_name):
    """
    Recursively return all item groups under a parent item group.
    Uses only `name` and `parent_item_group` which are valid fields.
    """
    groups = [parent_group_name]

    children = frappe.db.get_all(
        "Item Group", filters={"parent_item_group": parent_group_name}, fields=["name"]
    )

    for child in children:
        groups.append(child.name)
        # Add full path format "Parent/Child"
        full_path = f"{parent_group_name}/{child.name}"
        groups.append(full_path)
        # Recursively collect child groups
        groups.extend(_get_all_item_groups_under_parent(child.name))

    # Remove duplicates
    return list(dict.fromkeys(groups))


def _get_child_item_groups_only(parent_group_name):
    """
    Recursively return all child item groups under a parent item group.
    EXCLUDES the parent group itself - only returns descendants.

    Args:
            parent_group_name (str): Name of the parent item group

    Returns:
            list: List of child item group names (excluding parent)
    """
    child_groups = []

    children = frappe.db.get_all(
        "Item Group", filters={"parent_item_group": parent_group_name}, fields=["name"]
    )

    for child in children:
        child_groups.append(child.name)
        # Add full path format "Parent/Child"
        full_path = f"{parent_group_name}/{child.name}"
        child_groups.append(full_path)
        # Recursively collect child groups
        child_groups.extend(_get_child_item_groups_only(child.name))

    # Remove duplicates
    return list(dict.fromkeys(child_groups))


def _get_items_by_parent_group(
    parent_group_name, doctype, txt, searchfield, start, page_len, filters
):
    """
    Generic helper function to get items under a parent item group (including parent and all children).

    Args:
            parent_group_name (str): Name of the parent item group
            doctype (str): Doctype name (for query function signature)
            txt (str): Search text
            searchfield (str): Field to search in
            start (int): Pagination start
            page_len (int): Page length
            filters (dict): Additional filters

    Returns:
            list: List of item names
    """
    try:
        all_groups = _get_all_item_groups_under_parent(parent_group_name)

        if not all_groups:
            return []

        # Remove duplicates
        all_groups = list(dict.fromkeys(all_groups))

        placeholders = ",".join(["%s"] * len(all_groups))
        query = f"""
			SELECT DISTINCT i.name
			FROM `tabItem` i
			LEFT JOIN `tabItem Group` ig ON i.item_group = ig.name
			WHERE (
				i.item_group IN ({placeholders})
				OR i.item_group LIKE %s
				OR ig.parent_item_group IN ({placeholders})
			)
		"""

        # Parameters
        params = all_groups[:]  # for item_group IN
        params.append(f"{parent_group_name}/%")  # for full path LIKE
        params.extend(all_groups)  # for parent_item_group IN

        # Apply search text
        if txt:
            query += f" AND (i.{searchfield} LIKE %s OR i.item_name LIKE %s)"
            params.extend([f"%{txt}%", f"%{txt}%"])

        # Pagination
        query += " ORDER BY i.item_name LIMIT %s OFFSET %s"
        params.extend([page_len, start])

        result = frappe.db.sql(query, params, as_dict=False)

        return result
    except Exception as e:
        frappe.log_error(
            f"Error in _get_items_by_parent_group for {parent_group_name}: {str(e)}\n{frappe.get_traceback()}",
            "Get Items By Parent Group Error",
        )
        return []


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_stitching_items(doctype, txt, searchfield, start, page_len, filters):
    """
    Returns all items under the parent group 'Stitching'
    including children (e.g., 'Stitching/Curtain Stitching').
    """
    return _get_items_by_parent_group(
        "Stitching", doctype, txt, searchfield, start, page_len, filters
    )


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_fabric_items(doctype, txt, searchfield, start, page_len, filters):
    """
    Returns all items under the parent group 'Window Furnishings'
    including children (e.g., 'Window Furnishings/Main Fabric', 'Window Furnishings/Sheer Fabric').
    """
    return _get_items_by_parent_group(
        "Window Furnishings", doctype, txt, searchfield, start, page_len, filters
    )


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_lining_items_by_parent(doctype, txt, searchfield, start, page_len, filters):
    """
    Returns all items under the parent group 'Linings'
    including children (e.g., 'Linings/Basic Linings', 'Linings/Heavy Linings').
    """
    return _get_items_by_parent_group(
        "Linings", doctype, txt, searchfield, start, page_len, filters
    )


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_track_rod_items(doctype, txt, searchfield, start, page_len, filters):
    """
    Returns all items under the parent group 'Tracks & Rods'
    including children (e.g., 'Tracks & Rods/Tracks', 'Tracks & Rods/Rods').
    """
    return _get_items_by_parent_group(
        "Tracks & Rods", doctype, txt, searchfield, start, page_len, filters
    )


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_lead_rope_items(doctype, txt, searchfield, start, page_len, filters):
    """
    Returns all items under the parent group 'Stitching Accessories'
    including children (e.g., 'Stitching Accessories/Lead Rope', 'Stitching Accessories/Tapes').
    """
    return _get_items_by_parent_group(
        "Stitching Accessories", doctype, txt, searchfield, start, page_len, filters
    )


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_fitting_items(doctype, txt, searchfield, start, page_len, filters):
    """
    Returns all items under the parent group 'Labour'
    including children.
    """
    return _get_items_by_parent_group(
        "Labour", doctype, txt, searchfield, start, page_len, filters
    )


def _get_child_item_groups_only(parent_group_name):
    """
    Recursively return all child item groups under a parent item group.
    EXCLUDES the parent group itself - only returns descendants.

    Args:
            parent_group_name (str): Name of the parent item group

    Returns:
            list: List of child item group names (excluding parent)
    """
    child_groups = []

    children = frappe.db.get_all(
        "Item Group", filters={"parent_item_group": parent_group_name}, fields=["name"]
    )

    for child in children:
        child_groups.append(child.name)
        # Add full path format "Parent/Child"
        full_path = f"{parent_group_name}/{child.name}"
        child_groups.append(full_path)
        # Recursively collect child groups
        child_groups.extend(_get_child_item_groups_only(child.name))

    # Remove duplicates
    return list(dict.fromkeys(child_groups))


@frappe.whitelist()
def get_child_item_groups_of_stitching():
    """
    Get all child item groups (descendants) of "Stitching" parent group.
    Excludes "Stitching" itself - only returns child groups.

    Returns:
            list: List of child item group names
    """
    try:
        parent = "Stitching"
        child_groups = _get_child_item_groups_only(parent)
        return child_groups
    except Exception as e:
        frappe.log_error(
            f"Error in get_child_item_groups_of_stitching: {str(e)}\n{frappe.get_traceback()}",
            "Get Child Item Groups Error",
        )
        return []


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_lining_items(doctype, txt, searchfield, start, page_len, filters):
    """
    Returns all items that belong ONLY to child item groups of "Stitching".
    Excludes items directly under "Stitching" parent group.
    """
    try:
        parent = "Stitching"
        # Get only child groups (excluding parent)
        child_groups = _get_child_item_groups_only(parent)

        if not child_groups:
            return []

        # Remove duplicates
        child_groups = list(dict.fromkeys(child_groups))

        placeholders = ",".join(["%s"] * len(child_groups))
        query = f"""
			SELECT DISTINCT i.name
			FROM `tabItem` i
			LEFT JOIN `tabItem Group` ig ON i.item_group = ig.name
			WHERE (
				i.item_group IN ({placeholders})
				OR i.item_group LIKE %s
				OR ig.parent_item_group IN ({placeholders})
			)
			AND i.item_group != %s
		"""

        # Parameters
        params = child_groups[:]  # for item_group IN
        params.append(f"{parent}/%")  # for full path LIKE
        params.extend(child_groups)  # for parent_item_group IN
        params.append(parent)  # exclude parent group

        # Apply search text
        if txt:
            query += f" AND (i.{searchfield} LIKE %s OR i.item_name LIKE %s)"
            params.extend([f"%{txt}%", f"%{txt}%"])

        # Pagination
        query += " ORDER BY i.item_name LIMIT %s OFFSET %s"
        params.extend([page_len, start])

        result = frappe.db.sql(query, params, as_dict=False)

        return result
    except Exception as e:
        frappe.log_error(
            f"Error in get_lining_items: {str(e)}\n{frappe.get_traceback()}",
            "Lining Items Query Error",
        )
        return []
