import frappe # type: ignore


def send_customer_delivery_notification(doc, method=None):
    """
    Send email and WhatsApp notification to customer when Delivery Note is created.

    Args:
            doc (Document): Delivery Note document object
            method (str): Event method name (e.g., 'on_submit')

    Returns:
            None

    Raises:
            Exception: If notification sending fails
    """
    try:
        # Get customer email
        customer_email = get_customer_email(doc.customer, doc.get("contact_email"))
        if not customer_email:
            frappe.log_error(
                f"No email found for customer {doc.customer}",
                "Delivery Notification: Missing Customer Email",
            )
            return

        # Get customer name
        customer_name = (
            frappe.db.get_value("Customer", doc.customer, "customer_name")
            or doc.customer
        )

        # Build email subject
        subject = f" Your Order Has Been Delivered - {doc.name}"

        # Prepare delivery details
        delivery_date = (
            frappe.utils.formatdate(doc.posting_date) if doc.posting_date else "N/A"
        )
        delivery_time = (
            doc.posting_time
            if hasattr(doc, "posting_time") and doc.posting_time
            else ""
        )

        # Build items table rows
        items_rows = []
        total_qty = 0

        if doc.items:
            for idx, item in enumerate(doc.items, 1):
                item_name = (
                    frappe.db.get_value("Item", item.item_code, "item_name")
                    or item.item_code
                )
                qty = item.qty or 0
                total_qty += qty
                uom = item.uom or "Nos"

                items_rows.append(
                    f"""
					<tr>
						<td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: center; color: #6b7280; font-weight: 600;">{idx}</td>
						<td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">
							<strong style="color: #1f2937;">{frappe.utils.escape_html(item_name)}</strong><br>
							<span style="font-size: 12px; color: #6b7280;">Code: {frappe.utils.escape_html(item.item_code)}</span>
						</td>
						<td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: center;">
							<strong style="color: #1f2937;">{qty}</strong> <span style="font-size: 12px; color: #6b7280;">{frappe.utils.escape_html(uom)}</span>
						</td>
					</tr>
				"""
                )

        items_table_html = (
            "".join(items_rows)
            if items_rows
            else '<tr><td colspan="3" style="padding: 20px; text-align: center; color: #6b7280;">No items found</td></tr>'
        )

        # Prepare delivery information rows
        info_rows = []

        # Sales Order Reference
        if doc.items and doc.items[0].against_sales_order:
            sales_order = doc.items[0].against_sales_order
            info_rows.append(
                f"""
				<tr>
					<td style="padding: 8px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
						<strong style="color: #374151;">Sales Order</strong>
					</td>
					<td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">
						<span style="font-family: monospace; color: #1f2937;">{frappe.utils.escape_html(sales_order)}</span>
					</td>
				</tr>
			"""
            )

        # Delivery Date & Time
        datetime_display = f"{delivery_date}"
        if delivery_time:
            datetime_display += f" at {delivery_time}"

        info_rows.append(
            f"""
			<tr>
				<td style="padding: 8px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
					<strong style="color: #374151;">📅 Delivery Date</strong>
				</td>
				<td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">
					<span style="color: #1f2937; font-weight: 600;">{datetime_display}</span>
				</td>
			</tr>
		"""
        )

        # Total Items
        info_rows.append(
            f"""
			<tr>
				<td style="padding: 8px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
					<strong style="color: #374151;">📦 Total Items</strong>
				</td>
				<td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">
					<span style="color: #059669; font-weight: 600;">{len(doc.items)} items ({total_qty} quantity)</span>
				</td>
			</tr>
		"""
        )

        # Contact Person
        if doc.contact_person:
            contact_name = frappe.db.get_value(
                "Contact", doc.contact_person, "full_name"
            )
            contact_mobile = frappe.db.get_value(
                "Contact", doc.contact_person, "mobile_no"
            )

            contact_display = contact_name or ""
            if contact_mobile:
                contact_display += f" ({contact_mobile})"

            if contact_display:
                info_rows.append(
                    f"""
					<tr>
						<td style="padding: 8px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
							<strong style="color: #374151;">👤 Contact Person</strong>
						</td>
						<td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">
							<span style="color: #1f2937;">{frappe.utils.escape_html(contact_display)}</span>
						</td>
					</tr>
				"""
                )

        # Tracking/LR Number
        if hasattr(doc, "lr_no") and doc.lr_no:
            info_rows.append(
                f"""
				<tr>
					<td style="padding: 8px; background-color: #f9fafb;">
						<strong style="color: #374151;">🚚 Tracking Number</strong>
					</td>
					<td style="padding: 8px;">
						<span style="font-family: monospace; color: #1f2937; font-weight: 600;">{frappe.utils.escape_html(doc.lr_no)}</span>
					</td>
				</tr>
			"""
            )

        info_table_html = "".join(info_rows)

        # Build remarks section if available
        remarks_html = ""
        if hasattr(doc, "remarks") and doc.remarks:
            remarks_html = f"""
				<table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 16px;">
					<tr>
						<td style="background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px; border-radius: 4px;">
							<p style="margin: 0; color: #1e40af; font-size: 13px; line-height: 1.5;">
								<strong>📝 Delivery Notes:</strong><br>
								{frappe.utils.escape_html(doc.remarks)}
							</p>
						</td>
					</tr>
				</table>
			"""

        # Build the complete HTML message (Gmail-compatible)
        message = f"""
			<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f3f4f6; padding: 20px;">
				<!-- Header -->
				<table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px 8px 0 0; text-align: center;">
					<tr>
						<td style="padding: 24px;">
							<div style="background-color: white; width: 60px; height: 60px; border-radius: 50%; margin: 0 auto 12px; padding-top: 8px;">
								<span style="font-size: 28px;">✅</span>
							</div>
							<h1 style="margin: 0; color: white; font-size: 22px; font-weight: bold;">Order Delivered Successfully!</h1>
							<p style="margin: 6px 0 0; color: white; font-size: 14px;">Your order has been delivered</p>
						</td>
					</tr>
				</table>
				
				<!-- Main Content -->
				<table width="100%" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 0 0 8px 8px;">
					<tr>
						<td style="padding: 20px;">
							<!-- Greeting -->
							<p style="margin: 0 0 8px; font-size: 15px; color: #1f2937;">
								Dear <strong style="color: #10b981;">{frappe.utils.escape_html(customer_name)}</strong>,
							</p>
							<p style="margin: 0 0 16px; font-size: 14px; color: #4b5563; line-height: 1.5;">
								Your order has been successfully delivered. Thank you for choosing us!
							</p>
							
							<!-- Delivery Information -->
							<p style="margin: 0 0 8px; font-size: 14px; color: #374151; font-weight: bold;">📋 Delivery Information</p>
							<table width="100%" cellpadding="0" cellspacing="0" style="border: 1px solid #e5e7eb; border-radius: 4px; margin-bottom: 16px;">
								{info_table_html}
							</table>
							
							<!-- Items Delivered -->
							<p style="margin: 0 0 8px; font-size: 14px; color: #374151; font-weight: bold;">Items Delivered</p>
							<table width="100%" cellpadding="0" cellspacing="0" style="border: 1px solid #e5e7eb; border-radius: 4px; margin-bottom: 16px;">
								<tr style="background-color: #f9fafb;">
									<th style="padding: 8px; text-align: center; font-weight: bold; color: #374151; border-bottom: 2px solid #e5e7eb; width: 40px;">#</th>
									<th style="padding: 8px; text-align: left; font-weight: bold; color: #374151; border-bottom: 2px solid #e5e7eb;">Item</th>
									<th style="padding: 8px; text-align: center; font-weight: bold; color: #374151; border-bottom: 2px solid #e5e7eb; width: 80px;">Quantity</th>
								</tr>
								{items_table_html}
							</table>
							
							<!-- Remarks -->
							{remarks_html}							
							
						</td>
					</tr>				
				</table>			
			</div>
		"""

        # Send email
        frappe.sendmail(
            recipients=[customer_email],
            subject=subject,
            message=message,
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            attachments=(
                [
                    frappe.attach_print(
                        doc.doctype, doc.name, print_format="Standard", doc=doc
                    )
                ]
                if frappe.db.exists("Print Format", "Standard")
                else None
            ),
        )

        frappe.msgprint(
            msg=f"📧 Delivery notification sent to {customer_email}",
            title="Notification Sent",
            indicator="green",
        )

        # Log success
        frappe.logger().info(
            f"Delivery notification sent for {doc.name} to {customer_email}"
        )

    except Exception as e:
        # Log error but don't block delivery note submission
        frappe.log_error(
            message=frappe.get_traceback(),
            title=f"Delivery Notification Failed: {doc.name}",
        )
        frappe.logger().error(
            f"Failed to send delivery notification for {doc.name}: {str(e)}"
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


def update_additional_material_request_status(doc, method=None):
    """
    Update Material Request status to 'Issued' for material requests
    linked to the Sales Order when Delivery Note is submitted.

    Args:
            doc (Document): Delivery Note document object
            method (str): Event method name (e.g., 'on_submit')

    Returns:
            None

    Raises:
            Exception: If status update fails
    """
    try:
        # Get unique sales orders from delivery note items
        sales_orders = set()
        if doc.items:
            for item in doc.items:
                if item.against_sales_order:
                    sales_orders.add(item.against_sales_order)

        if not sales_orders:
            frappe.logger().info(f"No sales orders found in Delivery Note {doc.name}")
            return

        # Fetch material requests for each sales order where custom_is_additional = 1
        for sales_order in sales_orders:
            material_requests = frappe.get_all(
                "Material Request",
                filters={
                    "custom_sales_order": sales_order,
                    "custom_is_additional": 0,
                    "docstatus": 1,  # Only submitted material requests
                },
                fields=["name", "status"],
            )

            if not material_requests:
                frappe.logger().info(
                    f"No additional material requests found for Sales Order {sales_order}"
                )
                continue

            # Update status to 'Issued' for each material request
            for mr in material_requests:
                try:
                    # Get the material request document
                    mr_doc = frappe.get_doc("Material Request", mr.name)

                    # Update the status field and per_ordered to trigger 'Issued' status
                    mr_doc.status = "Issued"
                    mr_doc.per_ordered = 100.0
                    mr_doc.per_received = 100.0

                    # Use db_set to update multiple fields and trigger list view update
                    mr_doc.db_set(
                        {
                            "status": "Issued",
                            "per_ordered": 100.0,
                            "per_received": 100.0,
                        }
                    )

                    # Notify update to refresh list view
                    mr_doc.notify_update()

                    frappe.logger().info(
                        f"Updated Material Request {mr.name} status to 'Issued' for Sales Order {sales_order}"
                    )

                except Exception as e:
                    frappe.log_error(
                        message=f"Failed to update Material Request {mr.name}: {str(e)}\n{frappe.get_traceback()}",
                        title=f"Material Request Status Update Failed: {mr.name}",
                    )
                    frappe.logger().error(
                        f"Failed to update Material Request {mr.name}: {str(e)}"
                    )

            # Show success message to user
            if material_requests:
                frappe.msgprint(
                    msg=f"✅ Material request(s) status updated",
                    title="Material Requests Updated",
                    indicator="green",
                )

    except Exception as e:
        # Log error but don't block delivery note submission
        frappe.log_error(
            message=frappe.get_traceback(),
            title=f"Material Request Status Update Failed: {doc.name}",
        )
        frappe.logger().error(
            f"Failed to update material request status for Delivery Note {doc.name}: {str(e)}"
        )
