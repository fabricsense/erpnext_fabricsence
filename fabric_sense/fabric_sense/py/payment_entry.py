import frappe  # type: ignore
import json


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
    Update Contractor Payment History records when Payment Entry is submitted.

    For each row in custom_task_reference child table:
    - Fetch the corresponding contractor payment history record
    - Update Amount Paid field with allocated amount
    - Update Balance field with outstanding amount
    - Update status based on outstanding amount:
      - If outstanding <= 0: status = "Paid"
      - If outstanding > 0 and outstanding < grand_total: status = "Partially Paid"
      - If outstanding == grand_total: status = "Unpaid"

    Args:
        doc (Document): Payment Entry document object
        method (str): Event method name (e.g., 'on_submit')

    Returns:
        None
    """
    if not doc.custom_task_reference:
        return

    for row in doc.custom_task_reference:
        if not row.contractor_payment_history:
            continue

        try:
            # Fetch the contractor payment history record
            cph_doc = frappe.get_doc(
                "Contractor Payment History", row.contractor_payment_history
            )

            # Update Amount Paid field by adding allocated amount to existing value
            current_amount_paid = cph_doc.amount_paid or 0
            allocated_amount = row.allocated or 0
            cph_doc.amount_paid = current_amount_paid + allocated_amount

            # Update Balance field with outstanding amount
            cph_doc.balance = row.outstanding or 0

            # Determine status based on outstanding amount
            outstanding = row.outstanding or 0
            grand_total = row.grand_total or 0

            if outstanding <= 0:
                cph_doc.status = "Paid"
            elif outstanding > 0 and outstanding < grand_total:
                cph_doc.status = "Partially Paid"
            elif outstanding == grand_total:
                cph_doc.status = "Unpaid"
            else:
                # Default to Partially Paid for edge cases
                cph_doc.status = "Partially Paid"

            # Save the contractor payment history record
            cph_doc.save(ignore_permissions=True)

            frappe.db.commit()

        except Exception as e:
            frappe.log_error(
                message=f"Error updating Contractor Payment History {row.contractor_payment_history}: {str(e)}",
                title="Payment Entry - Contractor Payment History Update Error",
            )
            # Continue processing other records even if one fails
            continue


def revert_contractor_payment_history(doc, method=None):
    """
    Revert Contractor Payment History records when Payment Entry is cancelled.

    For each row in custom_task_reference child table:
    - Fetch the corresponding contractor payment history record
    - Revert Amount Paid field (subtract the allocated amount)
    - Recalculate Balance field (add back the allocated amount)
    - Update status based on new outstanding amount

    Args:
        doc (Document): Payment Entry document object
        method (str): Event method name (e.g., 'on_cancel')

    Returns:
        None
    """
    if not doc.custom_task_reference:
        return

    for row in doc.custom_task_reference:
        if not row.contractor_payment_history:
            continue

        try:
            # Fetch the contractor payment history record
            cph_doc = frappe.get_doc(
                "Contractor Payment History", row.contractor_payment_history
            )

            # Revert Amount Paid field (subtract the allocated amount)
            current_amount_paid = cph_doc.amount_paid or 0
            allocated_amount = row.allocated or 0
            cph_doc.amount_paid = max(0, current_amount_paid - allocated_amount)

            # Recalculate Balance field using the original amount
            original_amount = cph_doc.amount or 0
            cph_doc.balance = original_amount - cph_doc.amount_paid

            # Determine status based on new balance
            if cph_doc.balance <= 0:
                cph_doc.status = "Paid"
            elif cph_doc.balance > 0 and cph_doc.balance < original_amount:
                cph_doc.status = "Partially Paid"
            elif cph_doc.balance == original_amount:
                cph_doc.status = "Unpaid"
            else:
                # Default to Partially Paid for edge cases
                cph_doc.status = "Partially Paid"

            # Save the contractor payment history record
            cph_doc.save(ignore_permissions=True)

            frappe.db.commit()

        except Exception as e:
            frappe.log_error(
                message=f"Error reverting Contractor Payment History {row.contractor_payment_history}: {str(e)}",
                title="Payment Entry - Contractor Payment History Revert Error",
            )
            # Continue processing other records even if one fails
            continue


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
