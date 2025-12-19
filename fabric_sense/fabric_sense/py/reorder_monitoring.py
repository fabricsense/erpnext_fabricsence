# Copyright (c) 2025, innogenio and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, flt


def check_reorder_level_on_stock_change(doc, method=None):
    """
    Monitor stock changes and create reorder notifications when stock falls below reorder level.

    This function is triggered after Stock Ledger Entry submission to check if any item's
    stock has fallen below its defined reorder level for the specific warehouse.

    Args:
        doc (Document): Stock Ledger Entry document
        method (str): Event method name (e.g., 'on_submit')
    """
    try:
        # Only process if this is a stock reduction (negative actual_qty)
        if not doc.actual_qty or flt(doc.actual_qty) >= 0:
            return

        item_code = doc.item_code
        warehouse = doc.warehouse

        # Get current stock balance for this item in this warehouse
        # Pass the current SLE quantity to calculate actual stock after this transaction
        current_stock = get_current_stock_balance(item_code, warehouse, doc.actual_qty)

        # Get reorder level for this item-warehouse combination
        reorder_level = get_reorder_level(item_code, warehouse)

        if reorder_level is None:
            # No reorder level defined for this item-warehouse combination
            return

        # Debug logging
        frappe.logger().info(
            f"Reorder check for {item_code} in {warehouse}: "
            f"SLE qty: {doc.actual_qty}, Current stock: {current_stock}, "
            f"Reorder level: {reorder_level}"
        )

        # Check if current stock has fallen below reorder level
        if flt(current_stock) < flt(reorder_level):
            # Check if notification already exists for this item-warehouse combination
            # existing_notification = frappe.db.exists(
            #     "Reorder Notification",
            #     {
            #         "item": item_code,
            #         "warehouse": warehouse,
            #         "status": "Pending"
            #     }
            # )

            # if not existing_notification:
            # Create new reorder notification
            create_reorder_notification(
                item_code=item_code,
                warehouse=warehouse,
                reorder_level=reorder_level,
                current_quantity=current_stock,
            )

            frappe.logger().info(
                f"Reorder notification created for {item_code} in {warehouse}. "
                f"Current stock: {current_stock}, Reorder level: {reorder_level}"
            )

    except Exception as e:
        frappe.log_error(
            message=f"Error in reorder level monitoring: {str(e)}\n{frappe.get_traceback()}",
            title=f"Reorder Monitoring Error - Item: {doc.item_code}, Warehouse: {doc.warehouse}",
        )


def get_current_stock_balance(item_code, warehouse, current_sle_qty=0):
    """
    Get current stock balance for an item in a specific warehouse.
    
    Since this function is called during Stock Ledger Entry processing,
    we need to account for the current transaction's quantity to get the
    actual stock balance after the transaction.

    Args: 
        item_code (str): Item code
        warehouse (str): Warehouse name
        current_sle_qty (float): Current Stock Ledger Entry quantity to add

    Returns:
        float: Current stock balance after the transaction
    """
    try:
        # Get stock balance from Bin (before current transaction)
        bin_data = frappe.db.get_value(
            "Bin",
            {"item_code": item_code, "warehouse": warehouse},
            "actual_qty"
        )
        
        bin_qty = flt(bin_data) if bin_data is not None else 0.0
        
        # Add current Stock Ledger Entry quantity to get actual current stock
        current_stock = bin_qty + flt(current_sle_qty)
        
        # Debug logging
        frappe.logger().info(
            f"Stock calculation for {item_code} in {warehouse}: "
            f"Bin qty: {bin_qty}, SLE qty: {current_sle_qty}, "
            f"Calculated stock: {current_stock}"
        )
        
        return current_stock

    except Exception as e:
        frappe.log_error(
            message=f"Error getting stock balance: {str(e)}\n{frappe.get_traceback()}",
            title=f"Stock Balance Error - Item: {item_code}, Warehouse: {warehouse}",
        )
        
        # Final fallback: try to get from Bin directly and add current SLE qty
        try:
            bin_qty = frappe.db.get_value(
                "Bin",
                {"item_code": item_code, "warehouse": warehouse},
                "actual_qty"
            ) or 0.0
            return flt(bin_qty) + flt(current_sle_qty)
        except:
            return flt(current_sle_qty)


def get_reorder_level(item_code, warehouse):
    """
    Get reorder level for an item in a specific warehouse from Item's reorder levels child table.

    Args:
        item_code (str): Item code
        warehouse (str): Warehouse name

    Returns:
        float or None: Reorder level if defined, None otherwise
    """
    try:
        # Query the Item Reorder child table
        reorder_data = frappe.db.get_value(
            "Item Reorder",
            {"parent": item_code, "warehouse": warehouse},
            "warehouse_reorder_level",
        )

        if reorder_data:
            return flt(reorder_data)

        return None

    except Exception as e:
        frappe.log_error(
            message=f"Error getting reorder level: {str(e)}",
            title=f"Reorder Level Error - Item: {item_code}, Warehouse: {warehouse}",
        )
        return None


def create_reorder_notification(item_code, warehouse, reorder_level, current_quantity):
    """
    Create a new Reorder Notification record.

    Args:
        item_code (str): Item code
        warehouse (str): Warehouse name
        reorder_level (float): Defined reorder level
        current_quantity (float): Current stock quantity
    """
    try:
        # Create new Reorder Notification document
        reorder_notification = frappe.get_doc(
            {
                "doctype": "Reorder Notification",
                "item": item_code,
                "warehouse": warehouse,
                "reorder_level": str(
                    reorder_level
                ),  # Store as string as per field type
                "current_quantity": current_quantity,
                "date": today(),
                "status": "Pending",
            }
        )

        # Insert and submit the document
        reorder_notification.insert(ignore_permissions=True)

        # Log the creation
        frappe.logger().info(
            f"Reorder Notification created: {reorder_notification.name} for "
            f"Item: {item_code}, Warehouse: {warehouse}"
        )

    except Exception as e:
        frappe.log_error(
            message=f"Error creating reorder notification: {str(e)}\n{frappe.get_traceback()}",
            title=f"Reorder Notification Creation Error - Item: {item_code}, Warehouse: {warehouse}",
        )

@frappe.whitelist()
def mark_reorder_notification_as_read(notification_name):
    """
    Mark a reorder notification as read.

    Args:
        notification_name (str): Name of the Reorder Notification document
    """
    try:
        doc = frappe.get_doc("Reorder Notification", notification_name)
        doc.status = "Readed"
        doc.save(ignore_permissions=True)

        frappe.msgprint(_("Reorder notification marked as read."))

    except Exception as e:
        frappe.throw(_("Error marking notification as read: {0}").format(str(e)))


