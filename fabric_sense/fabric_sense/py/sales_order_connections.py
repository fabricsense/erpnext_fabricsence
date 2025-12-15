import frappe
from frappe import _


def get_measurement_sheet_connection(sales_order_name):
    """
    Get the Measurement Sheet connection for a Sales Order
    
    Args:
        sales_order_name: Name of the Sales Order
        
    Returns:
        Dict with Measurement Sheet connection data
    """
    try:
        # Get the Sales Order document
        sales_order = frappe.get_doc("Sales Order", sales_order_name)
        
        if not sales_order.measurement_sheet:
            return None
            
        # Check if the Measurement Sheet exists
        if frappe.db.exists("Measurement Sheet", sales_order.measurement_sheet):
            return {
                "doctype": "Measurement Sheet",
                "name": sales_order.measurement_sheet,
                "count": 1
            }
    except Exception:
        pass
        
    return None


@frappe.whitelist()
def get_sales_order_connections(doctype, name):
    """
    Get custom connections for Sales Order including Measurement Sheet
    
    Args:
        doctype: Should be "Sales Order"
        name: Name of the Sales Order document
        
    Returns:
        List of connection data
    """
    connections = []
    
    if doctype == "Sales Order":
        # Get Measurement Sheet connection
        ms_connection = get_measurement_sheet_connection(name)
        if ms_connection:
            connections.append({
                "label": _("Source Document"),
                "items": [ms_connection]
            })
    
    return connections
