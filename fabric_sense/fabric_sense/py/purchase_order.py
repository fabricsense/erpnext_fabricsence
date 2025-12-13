def send_vendor_po_notification(doc, method=None):
    """
    Send email and WhatsApp notification to vendor when Purchase Order is submitted.
    
    Args:
        doc (Document): Purchase Order document object
        method (str): Event method name (e.g., 'on_submit')
    
    Returns:
        None
    
    Raises:
        Exception: If notification sending fails
    """