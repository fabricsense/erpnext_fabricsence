# -*- coding: utf-8 -*-
# Copyright (c) 2024, Fabric Sense and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime, get_url, format_date, fmt_money, format_datetime


def send_customer_payment_notification(doc, method=None):
    """
    Send email notification to customer when Payment Entry is submitted.
    
    Args:
        doc (Document): Payment Entry document object
        method (str): Event method name (e.g., 'on_submit')
    """
    try:
        # Only send notification if payment is submitted
        if doc.docstatus != 1:
            return
        
        # Only notify for incoming payments (received from customers)
        if doc.payment_type != "Receive":
            return
        
        # Only notify if party type is Customer
        if doc.party_type != "Customer":
            return
        
        # Get customer email
        customer_email = get_customer_email(doc.party, doc.get("contact_email"))
        
        if not customer_email:
            frappe.msgprint(
                _("No email found for customer {0}. Payment notification not sent.").format(doc.party),
                indicator="orange",
                alert=True
            )
            frappe.log_error(
                f"No email found for customer {doc.party} in Payment Entry: {doc.name}",
                "Payment Notification Failed"
            )
            return
        
        # Send email notification
        email_sent = send_payment_email(doc, customer_email)
        
        # Log success
        if email_sent:
            frappe.log_error(
                f"Payment notification sent successfully for: {doc.name} to {customer_email}",
                "Payment Notification Success"
            )
        
    except Exception as e:
        frappe.log_error(
            f"Error in customer payment notification for {doc.name}: {str(e)}",
            "Payment Notification Error"
        )
        frappe.msgprint(
            _("Failed to send payment notification. Please check error logs."),
            indicator="red",
            alert=True
        )


def get_customer_email(customer, contact_email=None):
    """
    Get customer email from contact or customer master.
    
    Args:
        customer (str): Customer name
        contact_email (str): Contact email from Payment Entry
    
    Returns:
        str: Customer email address
    """
    # First try contact email from payment entry
    if contact_email:
        return contact_email
    
    # Try to get from customer contacts
    contacts = frappe.get_all(
        "Contact",
        filters={
            "link_doctype": "Customer",
            "link_name": customer
        },
        fields=["email_id", "is_primary_contact"],
        order_by="is_primary_contact desc"
    )
    
    if contacts and contacts[0].email_id:
        return contacts[0].email_id
    
    # Try to get from dynamic link
    contact_links = frappe.get_all(
        "Dynamic Link",
        filters={
            "link_doctype": "Customer",
            "link_name": customer,
            "parenttype": "Contact"
        },
        fields=["parent"]
    )
    
    if contact_links:
        contact = frappe.get_doc("Contact", contact_links[0].parent)
        if contact.email_id:
            return contact.email_id
    
    # Try customer master email field
    customer_doc = frappe.get_doc("Customer", customer)
    if customer_doc.get("email_id"):
        return customer_doc.email_id
    
    return None


def send_payment_email(doc, customer_email):
    """
    Send payment received notification email to customer.
    
    Args:
        doc (Document): Payment Entry document
        customer_email (str): Customer email address
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        # Get company details
        company = frappe.get_doc("Company", doc.company)
        company_email = company.email or frappe.db.get_single_value("System Settings", "email")
        
        # Get customer name
        customer = frappe.get_doc("Customer", doc.party)
        customer_name = customer.customer_name
        
        # Prepare invoice references table
        invoice_table_html = ""
        total_allocated = 0
        
        if doc.references:
            for ref in doc.references:
                if ref.reference_doctype == "Sales Invoice":
                    # Get invoice details
                    try:
                        invoice = frappe.get_doc("Sales Invoice", ref.reference_name)
                        outstanding_after = invoice.outstanding_amount
                        status_color = "#28a745" if outstanding_after == 0 else "#ffc107"
                        status_text = "PAID" if outstanding_after == 0 else "PARTIALLY PAID"
                        
                        # Main invoice row
                        invoice_table_html += f"""
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd;">{ref.reference_name}</td>
                            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{fmt_money(ref.total_amount, currency=doc.paid_to_account_currency)}</td>
                            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{fmt_money(ref.allocated_amount, currency=doc.paid_to_account_currency)}</td>
                            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{fmt_money(outstanding_after, currency=doc.paid_to_account_currency)}</td>
                            <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                                <span style="background-color: {status_color}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">
                                    {status_text}
                                </span>
                            </td>
                        </tr>
                        """
                        
                        # Add discount row if applicable
                        if invoice.get('discount_amount') and invoice.discount_amount > 0:
                            invoice_table_html += f"""
                        <tr style="background-color: #d4edda;">
                            <td colspan="5" style="padding: 8px; border: 1px solid #ddd;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: #155724; font-weight: 500;">Additional Discount ({invoice.additional_discount_percentage}%):</span>
                                    <span style="color: #155724; font-weight: bold;">- {fmt_money(invoice.discount_amount, currency=doc.paid_to_account_currency)}</span>
                                </div>
                            </td>
                        </tr>
                        """
                        
                        total_allocated += ref.allocated_amount
                    except:
                        invoice_table_html += f"""
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd;">{ref.reference_name}</td>
                            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{fmt_money(ref.total_amount, currency=doc.paid_to_account_currency)}</td>
                            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{fmt_money(ref.allocated_amount, currency=doc.paid_to_account_currency)}</td>
                            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">-</td>
                            <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">-</td>
                        </tr>
                        """
                        total_allocated += ref.allocated_amount
        
        # Payment method display
        payment_method = doc.mode_of_payment or "Bank Transfer"
        
        # Reference number display
        reference_info = ""
        if doc.reference_no:
            reference_info = f"""
            <tr>
                <td style="padding: 5px 0;"><strong>Transaction Reference:</strong></td>
                <td style="padding: 5px 0;">{doc.reference_no}</td>
            </tr>
            """
        if doc.reference_date:
            reference_info += f"""
            <tr>
                <td style="padding: 5px 0;"><strong>Transaction Date:</strong></td>
                <td style="padding: 5px 0;">{format_date(doc.reference_date)}</td>
            </tr>
            """
        
        # Get payment URL
        payment_url = get_url(doc.get_url())
        
        # Email subject
        subject = f"Payment Received - Receipt {doc.name}"
        
        # Email body
        message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
            <div style="background-color: #28a745; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
                <h2 style="margin: 0;">Payment Received Successfully</h2>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6;">
                <p style="font-size: 16px; margin: 0;">Dear {customer_name},</p>
                <p style="font-size: 16px; margin: 10px 0 0 0;">Thank you! We have successfully received your payment.</p>
            </div>
            
            <div style="background-color: #d4edda; padding: 20px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3 style="margin-top: 0; color: #155724;">Payment Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px 0; width: 40%;"><strong>Receipt Number:</strong></td>
                        <td style="padding: 5px 0;">{doc.name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>Payment Date:</strong></td>
                        <td style="padding: 5px 0;">{format_date(doc.posting_date)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>Payment Method:</strong></td>
                        <td style="padding: 5px 0;">{payment_method}</td>
                    </tr>
                    {reference_info}
                    <tr style="background-color: #c3e6cb;">
                        <td style="padding: 10px 0; font-size: 18px;"><strong>Amount Received:</strong></td>
                        <td style="padding: 10px 0; font-size: 20px; color: #155724;"><strong>{fmt_money(doc.paid_amount, currency=doc.paid_to_account_currency)}</strong></td>
                    </tr>
                </table>
            </div>
            
            {f'''
            <h3 style="color: #333; margin-top: 30px;">Invoice Payment Details</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <thead>
                    <tr style="background-color: #28a745; color: white;">
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Invoice Number</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Invoice Amount</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Payment Applied</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Outstanding</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {invoice_table_html}
                </tbody>
                <tfoot>
                    <tr style="background-color: #f8f9fa; font-weight: bold;">
                        <td colspan="2" style="padding: 10px; border: 1px solid #ddd; text-align: right;">Total Payment:</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{fmt_money(total_allocated, currency=doc.paid_to_account_currency)}</td>
                        <td colspan="2" style="padding: 10px; border: 1px solid #ddd;"></td>
                    </tr>
                </tfoot>
            </table>
            ''' if invoice_table_html else '<div style="background-color: #fff3cd; padding: 15px; margin: 20px 0; border-left: 4px solid #ffc107;"><p style="margin: 0;"><strong>Note:</strong> This payment has been recorded but not allocated to specific invoices. Please contact us if you need clarification.</p></div>'}
            
            <div style="background-color: #e7f3ff; padding: 15px; margin: 20px 0; border-left: 4px solid #007bff;">
                <h3 style="margin-top: 0; color: #004085;">What's Next?</h3>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    <li>Your payment has been applied to your account</li>
                    <li>Updated invoice(s) will reflect the payment</li>
                    <li>You can download this payment receipt for your records</li>
                    <li>A copy of this receipt has been recorded in our system</li>
                </ul>
            </div>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #ddd;">
                <p><strong>Need help or have questions?</strong></p>
                <p>Email: {company_email or 'N/A'}</p>
                {f"<p>Phone: {company.phone_no}</p>" if company.get('phone_no') else ""}
            </div>
            
            <div style="margin-top: 40px; padding: 20px; background-color: #f0f0f0; text-align: center; border-radius: 5px;">
                <p style="margin: 0; color: #666;">Thank you for your prompt payment!</p>
                <p style="margin: 5px 0; font-weight: bold; color: #28a745;">{company.company_name}</p>
                {f"<p style='margin: 5px 0; font-size: 12px; color: #666;'>{company.company_address}</p>" if company.get('company_address') else ""}
            </div>
            
            <div style="margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 5px; font-size: 11px; color: #666; text-align: center;">
                <p style="margin: 0;">This is an automated payment confirmation. Please do not reply to this email.</p>
                <p style="margin: 5px 0 0 0;">Please keep this receipt for your records.</p>
            </div>
        </div>
        """
        
        # Send email
        frappe.sendmail(
            recipients=[customer_email],
            subject=subject,
            message=message,
            reference_doctype="Payment Entry",
            reference_name=doc.name,
            delayed=False
        )
        
        frappe.msgprint(
            _("Payment receipt email sent to customer at {0}").format(customer_email),
            indicator="green",
            alert=True
        )
        
        return True
        
    except Exception as e:
        frappe.log_error(
            f"Error sending payment receipt email for {doc.name}: {str(e)}",
            "Payment Email Error"
        )
        frappe.msgprint(
            _("Failed to send payment receipt email. Check error log."),
            indicator="red",
            alert=True
        )
        return False