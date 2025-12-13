# -*- coding: utf-8 -*-
# Copyright (c) 2024, Fabric Sense and contributors
# For license information, please see license.txt

import frappe # type: ignore
from frappe import _ # type: ignore
from frappe.utils import now_datetime, get_url, format_date, fmt_money, getdate # type: ignore


def send_customer_invoice_notification(doc, method=None):
    """
    Send email notification to customer when Sales Invoice is submitted.
    
    Args:
        doc (Document): Sales Invoice document object
        method (str): Event method name (e.g., 'on_submit')
    """
    try:
        # Only send notification if invoice is submitted
        if doc.docstatus != 1:
            return
        
        # Get customer email
        customer_email = get_customer_email(doc.customer, doc.get("contact_email"))
        
        if not customer_email:
            frappe.msgprint(
                _("No email found for customer {0}. Email not sent.").format(doc.customer),
                indicator="orange",
                alert=True
            )
            frappe.log_error(
                f"No email found for customer {doc.customer} in Invoice: {doc.name}",
                "Customer Invoice Notification Failed"
            )
            return
        
        # Send email notification
        email_sent = send_invoice_email(doc, customer_email)
        
        # Log success
        if email_sent:
            frappe.log_error(
                f"Invoice email sent successfully for: {doc.name} to {customer_email}",
                "Invoice Notification Success"
            )
        
    except Exception as e:
        frappe.log_error(
            f"Error in customer invoice notification for {doc.name}: {str(e)}",
            "Invoice Notification Error"
        )
        frappe.msgprint(
            _("Failed to send invoice notification. Please check error logs."),
            indicator="red",
            alert=True
        )


def get_customer_email(customer, contact_email=None):
    """
    Get customer email from contact or customer master.
    
    Args:
        customer (str): Customer name
        contact_email (str): Contact email from Sales Invoice
    
    Returns:
        str: Customer email address
    """
    # First try contact email from invoice
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


def send_invoice_email(doc, customer_email):
    """
    Send invoice notification email to customer.
    
    Args:
        doc (Document): Sales Invoice document
        customer_email (str): Customer email address
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        # Get company details
        company = frappe.get_doc("Company", doc.company)
        company_email = company.email or frappe.db.get_single_value("System Settings", "email")
        
        # Get customer name
        customer = frappe.get_doc("Customer", doc.customer)
        customer_name = customer.customer_name
        
        # Prepare item table HTML
        item_table_html = ""
        for item in doc.items:
            item_table_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{item.item_name}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item.qty} {item.uom}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{fmt_money(item.rate, currency=doc.currency)}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{fmt_money(item.amount, currency=doc.currency)}</td>
            </tr>
            """
        
        # Calculate outstanding amount
        outstanding_amount = doc.outstanding_amount or doc.grand_total
        
        # Get invoice URL
        invoice_url = get_url(doc.get_url())
        
        # Get payment terms
        payment_terms = doc.payment_terms_template or "As per agreement"
        
        # Calculate due date
        due_date_str = "Upon receipt"
        if doc.due_date:
            due_date_str = format_date(doc.due_date)
            days_until_due = (getdate(doc.due_date) - getdate(doc.posting_date)).days
            if days_until_due > 0:
                due_date_str += f" ({days_until_due} days)"
        
        # Payment status badge
        payment_status_color = "#28a745" if doc.status == "Paid" else "#ffc107"
        payment_status = doc.status or "Unpaid"
        
        # Email subject
        subject = f"Invoice {doc.name} from {company.company_name}"
        
        # Email body
        message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
            <h2 style="color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px;">
                📄 Invoice Created
            </h2>
            
            <p>Dear {customer_name},</p>
            
            <p>Thank you for your business! Please find your invoice details below.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-left: 4px solid #007bff;">
                <h3 style="margin-top: 0; color: #007bff;">Invoice Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px 0; width: 40%;"><strong>Invoice Number:</strong></td>
                        <td style="padding: 5px 0;">{doc.name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>Invoice Date:</strong></td>
                        <td style="padding: 5px 0;">{format_date(doc.posting_date)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>Due Date:</strong></td>
                        <td style="padding: 5px 0; color: #dc3545; font-weight: bold;">{due_date_str}</td>
                    </tr>
                    {"<tr><td style='padding: 5px 0;'><strong>Sales Order:</strong></td><td style='padding: 5px 0;'>" + (doc.get('items')[0].sales_order or 'N/A') + "</td></tr>" if doc.get('items') and doc.items[0].get('sales_order') else ""}
                    <tr>
                        <td style="padding: 5px 0;"><strong>Payment Status:</strong></td>
                        <td style="padding: 5px 0;">
                            <span style="background-color: {payment_status_color}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 12px;">
                                {payment_status.upper()}
                            </span>
                        </td>
                    </tr>
                </table>
            </div>
            
            <h3 style="color: #333; margin-top: 30px;">Invoice Items</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <thead>
                    <tr style="background-color: #007bff; color: white;">
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Item</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Quantity</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Rate</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {item_table_html}
                </tbody>
                <tfoot>
                    <tr style="background-color: #f8f9fa; font-weight: bold;">
                        <td colspan="3" style="padding: 10px; border: 1px solid #ddd; text-align: right;">Total:</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{fmt_money(doc.total, currency=doc.currency)}</td>
                    </tr>
                    {f'<tr style="background-color: #f8f9fa;"><td colspan="3" style="padding: 10px; border: 1px solid #ddd; text-align: right;">Tax:</td><td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{fmt_money(doc.total_taxes_and_charges, currency=doc.currency)}</td></tr>' if doc.total_taxes_and_charges else ''}
                    {f'<tr style="background-color: #d4edda;"><td colspan="3" style="padding: 10px; border: 1px solid #ddd; text-align: right; color: #155724;"><strong>Additional Discount ({doc.additional_discount_percentage}%):</strong></td><td style="padding: 10px; border: 1px solid #ddd; text-align: right; color: #155724;"><strong>- {fmt_money(doc.discount_amount, currency=doc.currency)}</strong></td></tr>' if doc.get('discount_amount') and doc.discount_amount > 0 else ''}
                    <tr style="background-color: #007bff; color: white; font-size: 16px;">
                        <td colspan="3" style="padding: 12px; border: 1px solid #ddd; text-align: right;"><strong>Grand Total:</strong></td>
                        <td style="padding: 12px; border: 1px solid #ddd; text-align: right;"><strong>{fmt_money(doc.grand_total, currency=doc.currency)}</strong></td>
                    </tr>
                    {f'<tr style="background-color: #fff3cd;"><td colspan="3" style="padding: 10px; border: 1px solid #ddd; text-align: right; color: #856404;"><strong>Amount Due:</strong></td><td style="padding: 10px; border: 1px solid #ddd; text-align: right; color: #856404;"><strong>{fmt_money(outstanding_amount, currency=doc.currency)}</strong></td></tr>' if outstanding_amount > 0 else ''}
                </tfoot>
            </table>
            
            <div style="background-color: #fff3cd; padding: 15px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <h3 style="margin-top: 0; color: #856404;">💳 Payment Information</h3>
                <p><strong>Payment Terms:</strong> {payment_terms}</p>
                <p><strong>Amount to Pay:</strong> <span style="font-size: 20px; color: #dc3545; font-weight: bold;">{fmt_money(outstanding_amount, currency=doc.currency)}</span></p>
                {"<p style='margin-top: 10px; padding: 10px; background-color: #f8d7da; color: #721c24; border-radius: 5px;'><strong>⚠️ Please ensure payment by: " + due_date_str + "</strong></p>" if outstanding_amount > 0 else ""}
            </div>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #ddd;">
                <p><strong>For payment queries or support, please contact us</strong></p>
               
                {f"<p>📞 Phone: {company.phone_no}</p>" if company.get('phone_no') else ""}
            </div>
            
            <div style="margin-top: 40px; padding: 20px; background-color: #f0f0f0; text-align: center; border-radius: 5px;">
                <p style="margin: 0; color: #666;">Thank you for choosing us!</p>
                <p style="margin: 5px 0; font-weight: bold; color: #007bff;">Fabric Sense</p>
                {f"<p style='margin: 5px 0; font-size: 12px; color: #666;'>{company.company_address}</p>" if company.get('company_address') else ""}
            </div>
        </div>
        """
        
        # Send email
        frappe.sendmail(
            recipients=[customer_email],
            subject=subject,
            message=message,
            reference_doctype="Sales Invoice",
            reference_name=doc.name,
            delayed=False
        )
        
        frappe.msgprint(
            _("Invoice email sent to customer at {0}").format(customer_email),
            indicator="green",
            alert=True
        )
        
        return True
        
    except Exception as e:
        frappe.log_error(
            f"Error sending invoice email for {doc.name}: {str(e)}",
            "Invoice Email Error"
        )
        frappe.msgprint(
            _("Failed to send invoice email. Check error log."),
            indicator="red",
            alert=True
        )
        return False