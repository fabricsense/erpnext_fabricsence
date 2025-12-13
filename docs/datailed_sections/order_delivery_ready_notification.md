# Sales Order - Delivery Ready Notification

## Overview
- **Trigger(s)**:
  - Manual: User clicks "Send order ready notification" button in Sales Order form.
  - Button is available only for Sales Orders with status "To Deliver".
- **Action**: Send an email to the customer with delivery readiness details including expected delivery date.
- **Handler**: `fabric_sense/fabric_sense/py/sales_order.py: send_order_ready_notification()`

## Email Content
- **Subject**: `Your Order <Sales Order ID> is Ready for Delivery`
- **Body**: Modern, inline-styled HTML including:
  - Customer name (personalized greeting)
  - Order Number
  - Expected Delivery Date (formatted, or "To be confirmed" if not set)
  - Order Items table (Item name, Quantity with UOM, Rate, and Amount - all formatted with currency)
  - Company contact information (email, phone if available)

> The design uses a green theme (#28a745) to indicate readiness, matching the delivery-ready status.

## Recipient Resolution
Resolved by `get_customer_email(customer, contact_email)` with priority:
1. Contact email from Sales Order (`contact_email` parameter)
2. Primary Contact email from linked Customer contacts (`is_primary_contact` first)
3. Contact email from Dynamic Link (Customer → Contact)
4. Customer master email field (`Customer.email_id`)

If no email is found, the function displays a message and returns without blocking execution.

## Duplicate Email Prevention
- The function can be called multiple times via button click (no automatic prevention).
- Users can manually control when to send the notification by clicking the button.
- Each button click will send a new email notification.

## Process Flow
1. Sales Order status is set to "To Deliver" (manually or via workflow).
2. "Send order ready notification" button becomes available in the Sales Order form.
3. User clicks the button, which calls `send_order_ready_notification(sales_order_name)`.
4. Function retrieves the Sales Order document and resolves customer email using `get_customer_email()`.
5. If no email found, displays orange message and returns.
6. `send_delivery_ready_email(doc, customer_email)` builds the HTML email with:
   - Company details
   - Customer name
   - Delivery date (formatted)
   - Order items table (with Item, Quantity, Rate, and Amount columns)
   - Company contact information
7. Email is sent via `frappe.sendmail()` with reference to Sales Order.
8. Success message (green) is displayed to user showing recipient email.
9. Errors are logged via `frappe.log_error()` and error message (red) is displayed.

## File References
- Notification implementation: `fabric_sense/fabric_sense/py/sales_order.py`
  - Main function: `send_order_ready_notification()`
  - Email builder: `send_delivery_ready_email()`
  - Email resolver: `get_customer_email()`

## Usage
- **Via Button**: Click "Send order ready notification" button in Sales Order form (only visible when status is "To Deliver").
- **Via API** (if needed): `frappe.call("fabric_sense.fabric_sense.py.sales_order.send_order_ready_notification", {"sales_order": "SAL-ORD-00001"})`

## Troubleshooting
- **No email received**: 
  - Ensure the Customer has a resolvable email via the priority list above (Contact email → Primary Contact → Dynamic Link → Customer master).
  - Check if orange message appears indicating no email found for customer.
- **Button not visible**: 
  - Verify Sales Order status is "To Deliver" (button only appears for this status).
  - Check if button is properly configured in Sales Order form customization.
- **Email formatting issues**: 
  - The message uses inline CSS for better client compatibility.
  - Verify HTML rendering in email client.
- **Error message displayed**: 
  - Check error logs via "Error Log" doctype for detailed error information.
  - Verify Email Account configuration in System Settings.
  - Ensure email server/scheduler is running properly.
- **Function not working**: 
  - Verify the function is properly whitelisted (`@frappe.whitelist()` decorator).
  - Check browser console for JavaScript errors if button click fails.

