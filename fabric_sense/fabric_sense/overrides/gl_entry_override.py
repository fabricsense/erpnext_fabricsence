import frappe
from frappe import _
from erpnext.accounts.doctype.gl_entry.gl_entry import GLEntry


class CustomGLEntry(GLEntry):
    """
    Custom GL Entry class to override ERPNext's validation.
    Allows Expense Accounts with Party Type and Party for Employee payments.
    """
    
    def validate_party(self):
        """
        Override to allow Expense Account with Party Type and Party for Employee payments.
        
        ERPNext's original validation throws error: "Party Type and Party can only be set for Receivable / Payable account"
        This override allows Expense Account type for Employee payments from Payment Entry and Journal Entry.
        """
        # Check if this is an Employee payment with Expense Account
        if self.party_type and self.party:
            account_type = frappe.get_cached_value("Account", self.account, "account_type")
            
            # If account is Expense Account and party is Employee
            if account_type == "Indirect Expense" and self.party_type == "Employee":
                # Check if this is from a Payment Entry
                if self.voucher_type == "Payment Entry":
                    try:
                        # Get the Payment Entry to verify payment_type
                        payment_entry = frappe.get_cached_doc("Payment Entry", self.voucher_no)
                        
                        # If payment_type is "Pay", skip the parent validation
                        if payment_entry.payment_type == "Pay":
                            # Skip ERPNext's validation for this specific case
                            return
                    except Exception:
                        # If we can't get the payment entry, continue with normal validation
                        pass
                
                # Check if this is from a Journal Entry
                elif self.voucher_type == "Journal Entry":
                    # Allow Expense Account with Employee party for Journal Entry
                    # This is used for contractor expense tracking
                    return
        
        # For all other cases, call the parent class validation
        super(CustomGLEntry, self).validate_party()
