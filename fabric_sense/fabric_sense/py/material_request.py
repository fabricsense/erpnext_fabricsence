def validate_stock_availability(doc, method=None):
    """
    Validate stock availability for Material Request with Issue purpose.
    Show toast message if stock is insufficient.
    """

def check_if_additional_request(doc, method=None):
    """
    Check if this is an additional Material Request for the same Sales Order.
    Auto-set requires_manager_approval flag.
    """
    
def prevent_submission_without_approval(doc, method=None):
    """
    Prevent submission of Material Request if Manager approval is required but not given.
    """