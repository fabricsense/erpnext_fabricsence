def send_customer_invoice_notification(doc, method=None):
    """
    Send email and WhatsApp notification to customer when Sales Invoice is created.
    
    Args:
        doc (Document): Sales Invoice document object
        method (str): Event method name (e.g., 'on_submit')
    
    Returns:
        None
    
    Raises:
        Exception: If notification sending fails
    """

def send_order_ready_notification(sales_invoice_name):
    """
    Send order ready notification to customer.
    
    Args:
        sales_invoice_name (str): Name of the Sales Invoice
    
    Returns:
        dict: Success status and message
    """