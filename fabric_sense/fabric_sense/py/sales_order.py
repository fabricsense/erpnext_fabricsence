import frappe  # type: ignore
from frappe.model.mapper import get_mapped_doc  # type: ignore
from frappe import _  # type: ignore
from frappe.utils import format_date, fmt_money, get_url, flt  # type: ignore


def validate_billing_multiple(doc, method=None):
    """
    Validate that item quantities in Sales Order are multiples of their Billing Multiple.

    Args:
        doc (Document): Sales Order document object
        method (str): Event method name (e.g., 'validate')

    Raises:
        frappe.ValidationError: If any item quantity is not a multiple of its Billing Multiple
    """
    for item in doc.items:
        if not item.item_code:
            continue

        # Get Billing Multiple value from Item doctype
        billing_multiple = frappe.db.get_value(
            "Item", item.item_code, "custom_billing_multiples"
        )

        # If Billing Multiple exists and is greater than 0, validate quantity
        if billing_multiple and flt(billing_multiple) > 0:
            if flt(item.qty) % flt(billing_multiple) != 0:
                frappe.throw(
                    _(
                        "Quantity for item {0} must be a multiple of {1} (Billing Multiple). Current quantity: {2}"
                    ).format(
                        frappe.bold(item.item_name or item.item_code),
                        frappe.bold(billing_multiple),
                        frappe.bold(item.qty),
                    ),
                    title=_("Billing Multiple Validation Failed"),
                )


def validate_mbq(doc, method=None):
    """
    Validate Minimum Basic Quantity (MBQ) for items in Sales Order.

    Args:
        doc (Document): Sales Order document object
        method (str): Event method name (e.g., 'validate')

    Raises:
        frappe.ValidationError: If any item quantity is less than its MBQ
    """
    for item in doc.items:
        if not item.item_code:
            continue

        # Get MBQ value from Item doctype
        mbq = frappe.db.get_value("Item", item.item_code, "custom_mbq")

        # If MBQ exists and is greater than 0, validate quantity
        if mbq and mbq > 0:
            if item.qty < mbq:
                frappe.throw(
                    _(
                        "The given quantity of item {0} is less than the Minimum Basic Quantity (MBQ: {1})"
                    ).format(
                        frappe.bold(item.item_name or item.item_code), frappe.bold(mbq)
                    ),
                    title=_("MBQ Validation Failed"),
                )


def send_customer_approval_notification(doc, method=None):
    """
    Send email notification to customer when Sales Order manager approval status is updated to Approved.

    Args:
        doc (Document): Sales Order document object
        method (str): Event method name (e.g., 'on_update', 'on_submit')

    Returns:
        None

    Raises:
        Exception: If notification sending fails
    """
    try:
        # Check if manager_approval_status field exists and is set to "Approved"
        if not hasattr(doc, "manager_approval_status"):
            return
        
        # Only send notification if current status is "Approved"
        if doc.manager_approval_status != "Approved":
            return
        
        # Check if this is a new document (initial creation)
        if doc.is_new():
            return
        
        # Check if the status has actually changed in this update
        # This prevents duplicate emails when the document is saved multiple times while already approved
        if not doc.has_value_changed('manager_approval_status'):
            # Status hasn't changed, don't send email
            frappe.logger().debug(f"Sales Order {doc.name}: manager_approval_status has not changed, skipping email")
            return
        
        # Get the old value to check what it was before this update
        # Try _doc_before_save first, then fall back to database value
        old_value = None
        if hasattr(doc, '_doc_before_save') and doc._doc_before_save:
            old_value = doc._doc_before_save.get('manager_approval_status')
        else:
            # Fallback: get value from database
            old_value = frappe.db.get_value('Sales Order', doc.name, 'manager_approval_status')
        
        frappe.logger().debug(f"Sales Order {doc.name}: Old value = {old_value}, New value = {doc.manager_approval_status}")
        
        # Only send email if status changed FROM something else TO "Approved"
        # If it was already "Approved", don't send again
        if old_value == "Approved":
            frappe.logger().debug(f"Sales Order {doc.name}: Status was already Approved, skipping email")
            return
        
        frappe.logger().info(f"Sales Order {doc.name}: Status changed from {old_value} to Approved, sending email")
        
        # Get customer email
        customer_email = get_customer_email(doc.customer, doc.get("contact_email"))

        if not customer_email:
            frappe.msgprint(
                _("No email found for customer {0}. Email not sent.").format(
                    doc.customer
                ),
                indicator="orange",
                alert=True,
            )
            frappe.log_error(
                f"No email found for customer {doc.customer} in Sales Order: {doc.name}",
                "Sales Order Approval Notification Failed",
            )
            return

        # Send email notification
        email_sent = send_approval_email(doc, customer_email)

        # Log success
        if email_sent:
            frappe.logger().info(
                f"Sales Order approval email sent successfully for: {doc.name} to {customer_email}"
            )

    except Exception as e:
        frappe.log_error(
            f"Error in customer approval notification for {doc.name}: {str(e)}\n{frappe.get_traceback()}",
            "Sales Order Approval Notification Error",
        )
        frappe.msgprint(
            _("Failed to send approval notification. Please check error logs."),
            indicator="red",
            alert=True,
        )


def get_customer_email(customer, contact_email=None):
    """
    Get customer email from contact or customer master.

    Args:
        customer (str): Customer name
        contact_email (str): Contact email from Sales Order

    Returns:
        str: Customer email address
    """
    # First try contact email from sales order
    if contact_email:
        return contact_email

    # Try to get from customer contacts
    contacts = frappe.get_all(
        "Contact",
        filters={"link_doctype": "Customer", "link_name": customer},
        fields=["email_id", "is_primary_contact"],
        order_by="is_primary_contact desc",
    )

    if contacts and contacts[0].email_id:
        return contacts[0].email_id

    # Try to get from dynamic link
    contact_links = frappe.get_all(
        "Dynamic Link",
        filters={
            "link_doctype": "Customer",
            "link_name": customer,
            "parenttype": "Contact",
        },
        fields=["parent"],
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


def send_approval_email(doc, customer_email):
    """
    Send sales order approval notification email to customer.

    Args:
        doc (Document): Sales Order document
        customer_email (str): Customer email address

    Returns:
        bool: True if email sent successfully
    """
    try:
        # Get company details
        company = frappe.get_doc("Company", doc.company)

        # Get customer name
        customer = frappe.get_doc("Customer", doc.customer)
        customer_name = customer.customer_name

        # Prepare item table HTML
        item_table_html = ""
        for item in doc.items:
            item_table_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{frappe.utils.escape_html(item.item_name or item.item_code)}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item.qty} {item.uom}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{fmt_money(item.rate, currency=doc.currency)}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{fmt_money(item.amount, currency=doc.currency)}</td>
            </tr>
            """

        # Get delivery date
        delivery_date_str = (
            format_date(doc.delivery_date) if doc.delivery_date else "To be confirmed"
        )

        # Email subject
        subject = f"Sales Order {doc.name} Approved - {company.company_name}"

        # Email body
        message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                <div style="background-color: white; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 16px; padding-top: 16px;">
                    <span style="font-size: 40px;">✅</span>
                </div>
                <h1 style="color: white; margin: 0; font-size: 28px;">Sales Order Approved!</h1>
                <p style="color: white; margin: 10px 0 0; font-size: 16px;">Your order has been confirmed</p>
            </div>
            
            <div style="background-color: white; padding: 30px; border-radius: 0 0 8px 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <p style="font-size: 16px; color: #333;">Dear <strong style="color: #667eea;">{frappe.utils.escape_html(customer_name)}</strong>,</p>
                
                <p style="font-size: 14px; color: #666; line-height: 1.6;">
                    We are pleased to inform you that your sales order has been approved and is now being processed. 
                    Thank you for choosing us!
                </p>
                
                <div style="background-color: #f8f9fa; padding: 20px; margin: 25px 0; border-left: 4px solid #667eea; border-radius: 4px;">
                    <h3 style="margin-top: 0; color: #667eea; font-size: 18px;">📋 Order Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; width: 40%;"><strong>Order Number:</strong></td>
                            <td style="padding: 8px 0; font-family: monospace; color: #667eea; font-weight: bold;">{doc.name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Order Date:</strong></td>
                            <td style="padding: 8px 0;">{format_date(doc.transaction_date)}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Expected Delivery:</strong></td>
                            <td style="padding: 8px 0; color: #28a745; font-weight: bold;">{delivery_date_str}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Status:</strong></td>
                            <td style="padding: 8px 0;">
                                <span style="background-color: #28a745; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold;">
                                    APPROVED
                                </span>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <h3 style="color: #333; margin-top: 30px; font-size: 18px;">📦 Order Items</h3>
                <table style="width: 100%; border-collapse: collapse; margin: 15px 0; border: 1px solid #ddd;">
                    <thead>
                        <tr style="background-color: #667eea; color: white;">
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Item</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">Quantity</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: right;">Rate</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: right;">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {item_table_html}
                    </tbody>
                    <tfoot>
                        <tr style="background-color: #f8f9fa; font-weight: bold;">
                            <td colspan="3" style="padding: 12px; border: 1px solid #ddd; text-align: right;">Total:</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: right;">{fmt_money(doc.total, currency=doc.currency)}</td>
                        </tr>
                        {f'<tr style="background-color: #f8f9fa;"><td colspan="3" style="padding: 12px; border: 1px solid #ddd; text-align: right;">Tax:</td><td style="padding: 12px; border: 1px solid #ddd; text-align: right;">{fmt_money(doc.total_taxes_and_charges, currency=doc.currency)}</td></tr>' if doc.total_taxes_and_charges else ''}
                        {f'<tr style="background-color: #d4edda;"><td colspan="3" style="padding: 12px; border: 1px solid #ddd; text-align: right; color: #155724;"><strong>Discount ({doc.additional_discount_percentage}%):</strong></td><td style="padding: 12px; border: 1px solid #ddd; text-align: right; color: #155724;"><strong>- {fmt_money(doc.discount_amount, currency=doc.currency)}</strong></td></tr>' if doc.get('discount_amount') and doc.discount_amount > 0 else ''}
                        <tr style="background-color: #667eea; color: white; font-size: 16px;">
                            <td colspan="3" style="padding: 14px; border: 1px solid #ddd; text-align: right;"><strong>Grand Total:</strong></td>
                            <td style="padding: 14px; border: 1px solid #ddd; text-align: right;"><strong>{fmt_money(doc.grand_total, currency=doc.currency)}</strong></td>
                        </tr>
                    </tfoot>
                </table>
                
                <div style="background-color: #e7f3ff; padding: 20px; margin: 25px 0; border-left: 4px solid #2196F3; border-radius: 4px;">
                    <h3 style="margin-top: 0; color: #1976D2; font-size: 16px;">ℹ️ What's Next?</h3>
                    <ul style="margin: 10px 0; padding-left: 20px; color: #555; line-height: 1.8;">
                        <li>Your order is now being processed by our team</li>
                        <li>You will receive updates on the production and delivery status</li>
                        <li>Expected delivery date: <strong>{delivery_date_str}</strong></li>
                    </ul>
                </div>
                
                <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #ddd;">
                    <p style="margin: 0; color: #666;"><strong>Need assistance?</strong></p>
                    <p style="margin: 5px 0; color: #666;">Feel free to contact us for any queries regarding your order.</p>
                    {f"<p style='margin: 5px 0; color: #666;'>📞 Phone: {company.phone_no}</p>" if company.get('phone_no') else ""}
                    {f"<p style='margin: 5px 0; color: #666;'>📧 Email: {company.email}</p>" if company.get('email') else ""}
                </div>
                
                <div style="margin-top: 40px; padding: 20px; background-color: #f0f0f0; text-align: center; border-radius: 5px;">
                    <p style="margin: 0; color: #666;">Thank you for your business!</p>
                    <p style="margin: 5px 0; font-weight: bold; color: #667eea; font-size: 18px;">{company.company_name}</p>
                    {f"<p style='margin: 5px 0; font-size: 12px; color: #666;'>{company.company_address}</p>" if company.get('company_address') else ""}
                </div>
            </div>
        </div>
        """

        # Send email
        frappe.sendmail(
            recipients=[customer_email],
            subject=subject,
            message=message,
            reference_doctype="Sales Order",
            reference_name=doc.name,
            delayed=False,
        )

        frappe.msgprint(
            _("Sales Order approval email sent to customer at {0}").format(
                customer_email
            ),
            indicator="green",
            alert=True,
        )

        return True

    except Exception as e:
        frappe.log_error(
            f"Error sending approval email for {doc.name}: {str(e)}\n{frappe.get_traceback()}",
            "Sales Order Approval Email Error",
        )
        frappe.msgprint(
            _("Failed to send approval email. Check error log."),
            indicator="red",
            alert=True,
        )
        return False


def is_service_item(item_code):
    """
    Check if an item should be excluded from Material Request.
    Items are excluded if their parent item group is "Stitching" or "Labour".

    Args:
        item_code (str): Item code to check

    Returns:
        bool: True if item should be excluded (is a service item), False otherwise
    """
    try:
        # Get item's item_group
        item_group = frappe.db.get_value("Item", item_code, "item_group")
        if not item_group:
            return False

        # Check if item_group is "Stitching" or "Labour" (root level)
        if item_group in ["Stitching", "Labour"]:
            return True

        # Check if item_group starts with "Stitching/" or "Labour/" (child groups stored as paths)
        if item_group.startswith("Stitching/") or item_group.startswith("Labour/"):
            return True

        # Check parent_item_group if item_group is a child
        # In ERPNext, hierarchical item groups can be stored as "Parent/Child"
        # or we can check the parent_item_group field of the Item Group
        try:
            # Try to get Item Group by the full path first
            if frappe.db.exists("Item Group", item_group):
                item_group_doc = frappe.get_doc("Item Group", item_group)
                if (
                    hasattr(item_group_doc, "parent_item_group")
                    and item_group_doc.parent_item_group
                ):
                    parent_group = item_group_doc.parent_item_group
                    if parent_group in ["Stitching", "Labour"]:
                        return True
        except Exception:
            # If getting Item Group fails, try to extract parent from path
            # For paths like "Stitching/Curtain Stitching", check if first part is Stitching or Labour
            if "/" in item_group:
                parent_from_path = item_group.split("/")[0]
                if parent_from_path in ["Stitching", "Labour"]:
                    return True

        return False
    except Exception:
        # If there's any error checking, don't exclude the item
        return False


@frappe.whitelist()
def make_material_request(source_name, target_doc=None):
    """
    Create Material Request from Sales Order with custom Manager Approval Status logic.

    Logic:
    - If there are remaining items in the Sales Order that require a Material Request,
      set Manager Approval Status to "Approved"
    - If no items remain (all items already have Material Requests created),
      set Manager Approval Status to "Pending"
    - Service items (parent item group is "Stitching" or "Labour") are excluded

    Args:
        source_name (str): Sales Order name
        target_doc (Document): Target Material Request document (optional)

    Returns:
        Document: Material Request document
    """

    def set_missing_values(source, target):
        """Set missing values and calculate Manager Approval Status"""

        # Check if there are remaining items that need Material Request
        has_remaining_items = check_remaining_items(source_name)

        # Set Manager Approval Status based on remaining items
        if has_remaining_items:
            target.custom_manager_approval_status = "Approved"
        else:
            target.custom_manager_approval_status = "Pending"
            target.custom_is_additional = 1

        # Set Sales Order reference
        target.custom_sales_order = source_name

        # Run standard missing values method
        target.run_method("set_missing_values")

    def update_item(source, target, source_parent):
        """Update item quantities based on what's already been requested"""

        # Get the total quantity already requested for this item from this Sales Order
        requested_qty = (
            frappe.db.sql(
                """
            SELECT IFNULL(SUM(mri.qty), 0)
            FROM `tabMaterial Request Item` mri
            INNER JOIN `tabMaterial Request` mr ON mri.parent = mr.name
            WHERE mr.custom_sales_order = %s
                AND mri.item_code = %s
                AND mr.docstatus < 2
        """,
                (source_parent.name, source.item_code),
            )[0][0]
            or 0
        )

        # Calculate remaining quantity
        remaining_qty = source.qty - requested_qty

        # Set the quantity to remaining quantity
        target.qty = remaining_qty

        # Set schedule date from Sales Order delivery date
        target.schedule_date = source_parent.delivery_date

    def check_remaining_qty(source):
        """Check if item has remaining quantity to be requested"""

        # Exclude service items (parent item group is "Stitching" or "Labour")
        if is_service_item(source.item_code):
            return False

        # Get the total quantity already requested for this item from this Sales Order
        requested_qty = (
            frappe.db.sql(
                """
            SELECT IFNULL(SUM(mri.qty), 0)
            FROM `tabMaterial Request Item` mri
            INNER JOIN `tabMaterial Request` mr ON mri.parent = mr.name
            WHERE mr.custom_sales_order = %s
                AND mri.item_code = %s
                AND mr.docstatus < 2
        """,
                (source_name, source.item_code),
            )[0][0]
            or 0
        )

        # Calculate remaining quantity
        remaining_qty = source.qty - requested_qty

        # Only include items with remaining quantity > 0
        return remaining_qty > 0

    # Define the mapping
    doclist = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Material Request",
                "validation": {"docstatus": ["=", 1]},
                "field_map": {"name": "custom_sales_order"},
            },
            "Sales Order Item": {
                "doctype": "Material Request Item",
                "field_map": {
                    "name": "sales_order_item",
                    "parent": "sales_order",
                    "stock_uom": "uom",
                },
                "postprocess": update_item,
                "condition": check_remaining_qty,
            },
        },
        target_doc,
        set_missing_values,
    )

    return doclist


def check_remaining_items(sales_order_name):
    """
    Check if there are remaining items in the Sales Order that need Material Request.
    Excludes service items (items with parent item group "Stitching" or "Labour").

    Args:
        sales_order_name (str): Sales Order name

    Returns:
        bool: True if there are remaining non-service items, False otherwise
    """

    # Get all items from Sales Order with their quantities
    so_items = frappe.db.sql(
        """
        SELECT 
            soi.item_code,
            soi.qty as ordered_qty,
            IFNULL(SUM(mri.qty), 0) as requested_qty
        FROM `tabSales Order Item` soi
        LEFT JOIN `tabMaterial Request Item` mri 
            ON mri.item_code = soi.item_code 
            AND mri.sales_order = %s
        LEFT JOIN `tabMaterial Request` mr 
            ON mri.parent = mr.name 
            AND mr.docstatus < 2
        WHERE soi.parent = %s
        GROUP BY soi.item_code, soi.qty
    """,
        (sales_order_name, sales_order_name),
        as_dict=True,
    )

    # Check if any non-service item has remaining quantity
    for item in so_items:
        # Skip service items
        if is_service_item(item.item_code):
            continue
            
        remaining_qty = item.ordered_qty - item.requested_qty
        if remaining_qty > 0:
            return True

    return False


@frappe.whitelist()
def send_order_ready_notification(sales_order):
    """
    Send email notification when Sales Order is ready for delivery.

    Args:
        sales_order (str): Sales Order name
    """
    try:
        # Get Sales Order document
        doc = frappe.get_doc("Sales Order", sales_order)

        # Get customer email
        customer_email = get_customer_email(doc.customer, doc.get("contact_email"))

        if not customer_email:
            frappe.msgprint(
                _("No email found for customer {0}").format(doc.customer),
                indicator="orange",
                alert=True,
            )
            frappe.log_error(
                f"No email found for customer {doc.customer} in Sales Order: {doc.name}",
                "Order Ready Notification - No Email"
            )
            return False
        
        # Send email
        email_sent = send_delivery_ready_email(doc, customer_email)
        
        if email_sent:
            frappe.logger().info(
                f"Order ready notification sent successfully for: {doc.name} to {customer_email}"
            )
            return True
        else:
            frappe.logger().error(
                f"Failed to send order ready notification for: {doc.name}"
            )
            return False
        
    except Exception as e:
        frappe.log_error(
            f"Error sending order ready notification: {str(e)}\n{frappe.get_traceback()}",
            "Order Ready Notification Error"
        )
        frappe.msgprint(
            _("Failed to send notification. Check error log for details."),
            indicator="red",
            alert=True
        )
        return False


def get_customer_email(customer, contact_email=None):
    """Get customer email from contact or customer master"""
    # First try contact email from Sales Order
    if contact_email:
        return contact_email

    # Try to get from customer contacts
    contacts = frappe.get_all(
        "Contact",
        filters={"link_doctype": "Customer", "link_name": customer},
        fields=["email_id", "is_primary_contact"],
        order_by="is_primary_contact desc",
    )

    if contacts and contacts[0].email_id:
        return contacts[0].email_id

    # Try to get from dynamic link
    contact_links = frappe.get_all(
        "Dynamic Link",
        filters={
            "link_doctype": "Customer",
            "link_name": customer,
            "parenttype": "Contact",
        },
        fields=["parent"],
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


def send_delivery_ready_email(doc, customer_email):
    """
    Send delivery ready notification email.
    
    Args:
        doc (Document): Sales Order document
        customer_email (str): Customer email address
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        company = frappe.get_doc("Company", doc.company)
        company_email = company.email or frappe.db.get_single_value(
            "System Settings", "email"
        )
        customer = frappe.get_doc("Customer", doc.customer)
        customer_name = customer.customer_name
        subject = f"Your Order {doc.name} is Ready for Delivery"

        delivery_date_str = "To be confirmed"
        if doc.delivery_date:
            delivery_date_str = frappe.utils.format_date(doc.delivery_date)

        # Prepare item table HTML
        item_table_html = ""
        for item in doc.items:
            item_table_html += f"""
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">{frappe.utils.escape_html(item.item_name or item.item_code)}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item.qty} {item.uom}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{fmt_money(item.rate, currency=doc.currency)}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{fmt_money(item.amount, currency=doc.currency)}</td>
                    </tr>
            """

        # Email body
        message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
            <h2 style="color: #333; border-bottom: 2px solid #28a745; padding-bottom: 10px;">
                ✅ Order Ready for Delivery
            </h2>
            
            <p>Dear {frappe.utils.escape_html(customer_name)},</p>
            
            <p>Great news! Your order is ready for delivery.</p>
            
            <div style="background-color: #d4edda; padding: 15px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3 style="margin-top: 0; color: #155724;">Delivery Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px 0; width: 40%;"><strong>Order Number:</strong></td>
                        <td style="padding: 5px 0;">{doc.name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>Expected Delivery Date:</strong></td>
                        <td style="padding: 5px 0; color: #28a745; font-weight: bold; font-size: 16px;">{delivery_date_str}</td>
                    </tr>
                </table>
            </div>
            
            <h3 style="color: #333; margin-top: 30px;">Order Items</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <thead>
                    <tr style="background-color: #28a745; color: white;">
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
                    {f'<tr style="background-color: #d4edda;"><td colspan="3" style="padding: 10px; border: 1px solid #ddd; text-align: right; color: #155724;"><strong>Discount ({doc.additional_discount_percentage}%):</strong></td><td style="padding: 10px; border: 1px solid #ddd; text-align: right; color: #155724;"><strong>- {fmt_money(doc.discount_amount, currency=doc.currency)}</strong></td></tr>' if doc.get('discount_amount') and doc.discount_amount > 0 else ''}
                    <tr style="background-color: #28a745; color: white; font-size: 16px;">
                        <td colspan="3" style="padding: 12px; border: 1px solid #ddd; text-align: right;"><strong>Grand Total:</strong></td>
                        <td style="padding: 12px; border: 1px solid #ddd; text-align: right;"><strong>{fmt_money(doc.grand_total, currency=doc.currency)}</strong></td>
                    </tr>
                </tfoot>
            </table>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #ddd;">
                <p><strong>For delivery queries or support, please contact us:</strong></p>
                <p>📧 Email: {company_email or 'N/A'}</p>
                {f"<p>📞 Phone: {company.phone_no}</p>" if company.get('phone_no') else ""}
            </div>
            
            <div style="margin-top: 40px; padding: 20px; background-color: #f0f0f0; text-align: center; border-radius: 5px;">
                <p style="margin: 0; color: #666;">Thank you for choosing us!</p>
                <p style="margin: 5px 0; font-weight: bold; color: #28a745;">{company.company_name}</p>
                {f"<p style='margin: 5px 0; font-size: 12px; color: #666;'>{frappe.utils.escape_html(company.company_address)}</p>" if company.get('company_address') else ""}
            </div>
            
            <div style="margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 5px; font-size: 11px; color: #666; text-align: center;">
                <p style="margin: 0;">This is a system-generated email. Please do not reply to this email.</p>
            </div>
        </div>
        """

        frappe.sendmail(
            recipients=[customer_email],
            subject=subject,
            message=message,
            reference_doctype="Sales Order",
            reference_name=doc.name,
            delayed=False
        )

        frappe.msgprint(
            _("Delivery ready notification sent to {0}").format(customer_email),
            indicator="green",
            alert=True,
        )
        
        return True
        
    except Exception as e:
        frappe.log_error(
            f"Error sending delivery ready email for Sales Order {doc.name}: {str(e)}\n{frappe.get_traceback()}",
            "Sales Order Delivery Ready Email Error",
        )
        frappe.msgprint(
            _("Failed to send delivery notification. Check error log for details."),
            indicator="red",
            alert=True
        )
        return False


@frappe.whitelist()
def create_multi_material_request(sales_order):
    """
    Create two Material Requests from Sales Order:
    - Purchase type: for items with 'Is On Order Item' checked
    - Material Issue type: for all other items
    
    Args:
        sales_order (str): Sales Order name
        
    Returns:
        dict: Contains purchase_mr and issue_mr names
    """
    try:
        # Get the Sales Order document
        so_doc = frappe.get_doc("Sales Order", sales_order)
        
        if so_doc.docstatus != 1:
            frappe.throw(_("Sales Order must be submitted to create Material Requests"))
        
        # Separate items based on 'Is On Order Item' field
        purchase_items = []
        issue_items = []
        
        for item in so_doc.items:
            # Skip service items
            if is_service_item(item.item_code):
                continue
            
            # Check if item has 'Is On Order Item' checked
            is_on_order = frappe.db.get_value("Item", item.item_code, "custom_is_onorder_item")
            
            if is_on_order:
                purchase_items.append(item)
            else:
                issue_items.append(item)
        
        result = {
            "purchase_mr": None,
            "issue_mr": None
        }
        
        # Create Purchase Material Request if there are on-order items
        if purchase_items:
            purchase_mr = create_material_request_from_items(
                so_doc, 
                purchase_items, 
                "Purchase"
            )
            if purchase_mr:
                result["purchase_mr"] = purchase_mr.name
        
        # Create Material Issue Request for other items
        if issue_items:
            issue_mr = create_material_request_from_items(
                so_doc, 
                issue_items, 
                "Material Issue"
            )
            if issue_mr:
                result["issue_mr"] = issue_mr.name
        
        return result
        
    except Exception as e:
        frappe.log_error(
            f"Error creating multi material request for {sales_order}: {str(e)}\n{frappe.get_traceback()}",
            "Multi Material Request Error"
        )
        frappe.throw(_("Error creating Material Requests: {0}").format(str(e)))


def create_material_request_from_items(so_doc, items, material_request_type):
    """
    Create a Material Request from given items.
    
    Args:
        so_doc (Document): Sales Order document
        items (list): List of Sales Order Item rows
        material_request_type (str): "Purchase" or "Material Issue"
        
    Returns:
        Document: Created Material Request document or None
    """
    if not items:
        return None
    
    try:
        # Create Material Request
        mr_doc = frappe.new_doc("Material Request")
        mr_doc.material_request_type = material_request_type
        mr_doc.transaction_date = frappe.utils.today()
        mr_doc.schedule_date = so_doc.delivery_date or frappe.utils.today()
        mr_doc.company = so_doc.company
        mr_doc.custom_sales_order = so_doc.name
        
        # Set approval status based on whether it's first or additional request
        has_remaining_items = check_remaining_items(so_doc.name)
        if has_remaining_items:
            mr_doc.custom_manager_approval_status = "Approved"
        else:
            mr_doc.custom_manager_approval_status = "Pending"
            mr_doc.custom_is_additional = 1
        
        # Add items to Material Request
        for item in items:
            mr_doc.append("items", {
                "item_code": item.item_code,
                "qty": item.qty,
                "uom": item.stock_uom or item.uom,
                "schedule_date": so_doc.delivery_date or frappe.utils.today(),
                "warehouse": item.warehouse,
                "sales_order": so_doc.name,
                "sales_order_item": item.name
            })
        
        mr_doc.insert()
        mr_doc.submit()
        
        frappe.db.commit()
        
        return mr_doc
        
    except Exception as e:
        frappe.log_error(
            f"Error creating {material_request_type} Material Request: {str(e)}\n{frappe.get_traceback()}",
            f"Create {material_request_type} MR Error"
        )
        return None
