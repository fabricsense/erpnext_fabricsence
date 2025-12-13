def set_manager_approval_status_for_deductions(doc, method=None):
    """
    Automatically set manager approval status to 'Discount Approval Pending'
    if Payment Deductions or Loss child table has records.

    Args:
        doc (Document): Payment Entry document object
        method (str): Event method name (e.g., 'validate')

    Returns:
        None
    """
    # Check if deductions table has any records
    if (
        doc.deductions
        and len(doc.deductions) > 0
        and doc.custom_manager_approval_status == "Pending"
    ):
        doc.custom_manager_approval_status = "Discount Approval Pending"


def send_customer_payment_notification(doc, method=None):
    """
    Send email and WhatsApp notification to customer when Payment Entry is submitted.

    Args:
        doc (Document): Payment Entry document object
        method (str): Event method name (e.g., 'on_submit')

    Returns:
        None

    Raises:
        Exception: If notification sending fails
    """
