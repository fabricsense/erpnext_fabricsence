# -*- coding: utf-8 -*-
# Copyright (c) 2024, Fabric Sense and contributors
# For license information, please see license.txt

import frappe # type: ignore
from frappe import _ # type: ignore
from frappe.utils import now_datetime, get_url, format_date, fmt_money # type: ignore


def send_vendor_po_notification(doc, method=None):
    """
    Send email notification to vendor when Purchase Order is created.
    
    Args:
        doc (Document): Purchase Order document object
        method (str): Event method name (e.g., 'on_submit')
    
    Returns:
        None
    
    Raises:
        Exception: If notification sending fails
    """
    try:
        # Only send notification if PO is submitted
        if doc.docstatus != 1:
            return
        
        # Get vendor details
        vendor = frappe.get_doc("Supplier", doc.supplier)
        
        # Get vendor contact email
        vendor_email = get_vendor_email(doc.supplier, doc.get("contact_email"))
        
        if not vendor_email:
            frappe.msgprint(
                _("No email found for vendor {0}. Email not sent.").format(doc.supplier),
                indicator="orange",
                alert=True
            )
            frappe.log_error(
                f"No email found for vendor {doc.supplier} in PO: {doc.name}",
                "Vendor Notification Failed"
            )
            return
        
        # Send email notification
        email_sent = send_email_notification(doc, vendor_email, vendor.supplier_name)
        
        # Log success
        if email_sent:
            frappe.log_error(
                f"Email sent successfully for PO: {doc.name} to {vendor_email}",
                "PO Notification Success"
            )
        
    except Exception as e:
        frappe.log_error(
            f"Error in vendor notification for PO {doc.name}: {str(e)}",
            "Vendor Notification Error"
        )
        frappe.msgprint(
            _("Failed to send vendor notification. Please check error logs."),
            indicator="red",
            alert=True
        )


def get_vendor_email(supplier, contact_email=None):
    """
    Get vendor email from contact or supplier master.
    
    Args:
        supplier (str): Supplier name
        contact_email (str): Contact email from PO
    
    Returns:
        str: Vendor email address
    """
    # First try contact email from PO
    if contact_email:
        return contact_email
    
    # Try to get from supplier contacts
    contacts = frappe.get_all(
        "Contact",
        filters={
            "link_doctype": "Supplier",
            "link_name": supplier
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
            "link_doctype": "Supplier",
            "link_name": supplier,
            "parenttype": "Contact"
        },
        fields=["parent"]
    )
    
    if contact_links:
        contact = frappe.get_doc("Contact", contact_links[0].parent)
        if contact.email_id:
            return contact.email_id
    
    return None


def send_email_notification(doc, vendor_email, vendor_name):
    """
    Send email notification to vendor.
    
    Args:
        doc (Document): Purchase Order document
        vendor_email (str): Vendor email address
        vendor_name (str): Vendor name
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        # Get company details
        company = frappe.get_doc("Company", doc.company)
        company_email = company.email or frappe.db.get_single_value("System Settings", "email")
        
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
        
        # Get PO URL
        po_url = get_url(doc.get_url())
        
        # Get delivery address
        delivery_address = "To be confirmed"
        if doc.shipping_address_display:
            delivery_address = doc.shipping_address_display
        
        # Email subject
        subject = f"Purchase Order {doc.name} created"
        
        # Email body
        message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
            <h2 style="color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 10px;">
                Purchase Order Created
            </h2>
            
            <p>Dear {vendor_name},</p>
            
            <p>We are pleased to place the following purchase order with you.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-left: 4px solid #0066cc;">
                <h3 style="margin-top: 0; color: #0066cc;">Purchase Order Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px 0;"><strong>PO Number:</strong></td>
                        <td style="padding: 5px 0;">{doc.name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>PO Date:</strong></td>
                        <td style="padding: 5px 0;">{format_date(doc.transaction_date)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>Required By:</strong></td>
                        <td style="padding: 5px 0;">{format_date(doc.schedule_date) if doc.schedule_date else 'As per item schedule'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>Total Amount:</strong></td>
                        <td style="padding: 5px 0; font-size: 18px; color: #0066cc;"><strong>{fmt_money(doc.grand_total, currency=doc.currency)}</strong></td>
                    </tr>
                </table>
            </div>
            
            <h3 style="color: #333; margin-top: 30px;">Items Ordered</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <thead>
                    <tr style="background-color: #0066cc; color: white;">
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Item</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Quantity</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Rate</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {item_table_html}
                </tbody>
            </table>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #ddd;">
                <p><strong>Please confirm receipt of this order and provide the following:</strong></p>
                <ul>
                    <li>Order acknowledgment</li>
                    <li>Expected delivery date</li>
                    <li>Proforma invoice (if applicable)</li>
                </ul>
                
                <p style="margin-top: 20px;">If you have any questions or concerns, please contact us</p>
            </div>
            
            <div style="margin-top: 40px; padding: 20px; background-color: #f0f0f0; text-align: center; border-radius: 5px;">
                <p style="margin: 0; color: #666;">Thank you for your business partnership!</p>
                <p style="margin: 5px 0; font-weight: bold; color: #0066cc;">Fabric Sense</p>
            </div>
        </div>
        """
        
        # Send email
        frappe.sendmail(
            recipients=[vendor_email],
            subject=subject,
            message=message,
            reference_doctype="Purchase Order",
            reference_name=doc.name,
            delayed=False
        )
        
        frappe.msgprint(
            _("Email sent to vendor at {0}").format(vendor_email),
            indicator="green",
            alert=True
        )
        
        return True
        
    except Exception as e:
        frappe.log_error(
            f"Error sending email to vendor for PO {doc.name}: {str(e)}",
            "Vendor Email Error"
        )
        frappe.msgprint(
            _("Failed to send email to vendor. Check error log."),
            indicator="red",
            alert=True
        )
        return False