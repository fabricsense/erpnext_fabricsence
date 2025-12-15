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


def update_contractor_payment_history(doc, method=None):
    """
    Update Contractor Payment History status and amount when Payment Entry is submitted.
    Handles both single record (via custom_contractor_payment_history field) and 
    multiple records (via custom_contractor_payment_records_json field).

    Args:
        doc (Document): Payment Entry document object
        method (str): Event method name (e.g., 'on_submit')

    Returns:
        None
    """
    import frappe
    import json
    
    updated_records = []
    
    # First, check if there are multiple records in the JSON field
    records_json = getattr(doc, 'custom_contractor_payment_records_json', None)
    
    if records_json:
        try:
            records = json.loads(records_json)
            if records and len(records) > 0:
                for record in records:
                    record_name = record.get('name') if isinstance(record, dict) else record
                    if record_name:
                        try:
                            # Get the Contractor Payment History document
                            cph_doc = frappe.get_doc("Contractor Payment History", record_name)
                            
                            # Update the status to Paid and set amount paid equal to balance
                            cph_doc.status = "Paid"
                            cph_doc.amount_paid = cph_doc.amount  # Pay the full amount
                            cph_doc.payment_entry = doc.name
                            
                            # Save the document
                            cph_doc.save(ignore_permissions=True)
                            updated_records.append(cph_doc.name)
                            
                        except Exception as e:
                            frappe.log_error(f"Error updating Contractor Payment History {record_name}: {str(e)}")
                
                if updated_records:
                    frappe.msgprint(f"Updated {len(updated_records)} Contractor Payment History record(s) to Paid status: {', '.join(updated_records)}")
                return  # Exit after processing JSON records
        except json.JSONDecodeError as e:
            frappe.log_error(f"Error parsing contractor payment records JSON: {str(e)}")
    
    # Fallback: Check single record link (for backward compatibility)
    if getattr(doc, 'custom_contractor_payment_history', None) and not updated_records:
        try:
            # Get the Contractor Payment History document
            cph_doc = frappe.get_doc("Contractor Payment History", doc.custom_contractor_payment_history)
            
            # Update the status to Paid and set amount paid
            cph_doc.status = "Paid"
            cph_doc.amount_paid = doc.paid_amount
            cph_doc.payment_entry = doc.name
            
            # Save the document
            cph_doc.save(ignore_permissions=True)
            
            frappe.msgprint(f"Contractor Payment History {cph_doc.name} updated to Paid status")
            
        except Exception as e:
            frappe.log_error(f"Error updating Contractor Payment History: {str(e)}")


def revert_contractor_payment_history(doc, method=None):
    """
    Revert Contractor Payment History status to Unpaid when Payment Entry is cancelled.
    Handles both single record (via custom_contractor_payment_history field) and 
    multiple records (via custom_contractor_payment_records_json field).

    Args:
        doc (Document): Payment Entry document object
        method (str): Event method name (e.g., 'on_cancel')

    Returns:
        None
    """
    import frappe
    import json
    
    reverted_records = []
    
    # First, check if there are multiple records in the JSON field
    records_json = getattr(doc, 'custom_contractor_payment_records_json', None)
    
    if records_json:
        try:
            records = json.loads(records_json)
            if records and len(records) > 0:
                for record in records:
                    record_name = record.get('name') if isinstance(record, dict) else record
                    if record_name:
                        try:
                            # Get the Contractor Payment History document
                            cph_doc = frappe.get_doc("Contractor Payment History", record_name)
                            
                            # Revert the status to Unpaid and clear amount paid
                            cph_doc.status = "Unpaid"
                            cph_doc.amount_paid = 0
                            cph_doc.payment_entry = None
                            
                            # Save the document
                            cph_doc.save(ignore_permissions=True)
                            reverted_records.append(cph_doc.name)
                            
                        except Exception as e:
                            frappe.log_error(f"Error reverting Contractor Payment History {record_name}: {str(e)}")
                
                if reverted_records:
                    frappe.msgprint(f"Reverted {len(reverted_records)} Contractor Payment History record(s) to Unpaid status: {', '.join(reverted_records)}")
                return  # Exit after processing JSON records
        except json.JSONDecodeError as e:
            frappe.log_error(f"Error parsing contractor payment records JSON: {str(e)}")
    
    # Fallback: Check single record link (for backward compatibility)
    if getattr(doc, 'custom_contractor_payment_history', None) and not reverted_records:
        try:
            # Get the Contractor Payment History document
            cph_doc = frappe.get_doc("Contractor Payment History", doc.custom_contractor_payment_history)
            
            # Revert the status to Unpaid and clear amount paid
            cph_doc.status = "Unpaid"
            cph_doc.amount_paid = 0
            cph_doc.payment_entry = None
            
            # Save the document
            cph_doc.save(ignore_permissions=True)
            
            frappe.msgprint(f"Contractor Payment History {cph_doc.name} reverted to Unpaid status")
            
        except Exception as e:
            frappe.log_error(f"Error reverting Contractor Payment History: {str(e)}")


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
