# Sales Invoice and Delivery Note Creation Guidelines

## Overview

This guide covers the creation and workflow management of Sales Invoices and Delivery Notes in the Fabric Sense application. Sales Invoices are created corresponding to approved Sales Orders to bill customers, and Delivery Notes are created to record the delivery of goods. Both documents utilize ERPNext's default doctypes with customizations for notifications and workflow enhancements.

---

## Sales Invoice Creation

### Prerequisites

A Sales Invoice can **only** be created when:

1. **Sales Order Status = "Approved"**
   - The Sales Order must be in the "Approved" state
   - Manager has reviewed and approved the order
   - Material requirements have been fulfilled

2. **Items Ready for Billing**
   - Items are available in stock or have been received
   - Material Requests have been processed
   - For stitched curtains: Tailoring work is completed

3. **Customer Record Valid**
   - Customer billing address is configured
   - Payment terms are defined
   - Credit limit is verified (if applicable)

---

## Using Default Sales Invoice Doctype

ERPNext's standard **Sales Invoice** doctype provides comprehensive functionality for customer billing:

### Standard Features Available

- **Invoice Management**: Create and track customer invoices
- **Item Details**: Multiple items with quantities, rates, and amounts
- **Tax Calculation**: Automatic tax computation based on tax templates
- **Payment Terms**: Configure payment schedules and due dates
- **Accounting Integration**: Automatic posting to Chart of Accounts
- **Status Tracking**: Draft, Submitted, Paid, Unpaid, Overdue, Cancelled
- **Document Links**: Links to Sales Orders, Delivery Notes, Payment Entries
- **Print Formats**: Professional invoice templates

### Standard Fields Used

| Field Name | Field Type | Description | Usage in Fabric Sense |
|------------|-----------|-------------|----------------------|
| `customer` | Link (Customer) | Customer reference | Auto-populated from Sales Order |
| `posting_date` | Date | Invoice date | Date when invoice is created |
| `due_date` | Date | Payment due date | Calculated based on payment terms |
| `items` | Table | Invoice items | Auto-populated from Sales Order |
| `total` | Currency | Total amount | Auto-calculated |
| `grand_total` | Currency | Final amount with taxes | Auto-calculated |
| `outstanding_amount` | Currency | Amount pending | Updated on payment |
| `status` | Select | Invoice status | System-controlled |
| `sales_order` | Link | Reference to Sales Order | Links to originating SO |

---

## Creating Sales Invoice from Sales Order

### User Journey - Salesperson

#### Step 1: Open Approved Sales Order
- Navigate to the approved Sales Order
- Verify all items are ready for billing
- Check if material requests are fulfilled
- For stitched orders: Confirm tailoring is complete

#### Step 2: Click "Create Sales Invoice" Button
- ERPNext provides a standard "Create" button
- Select "Sales Invoice" from the dropdown
- System opens new Sales Invoice form

#### Step 3: Sales Invoice Auto-Population
- System creates a new Sales Invoice with:
  - Customer details from Sales Order
  - All items from Sales Order
  - Quantities and rates pre-filled
  - Taxes and charges applied
  - Total amounts calculated
  - Sales Order reference linked

#### Step 4: Review and Adjust
- Salesperson reviews the auto-populated data
- Verify item quantities and rates
- Check tax calculations
- Adjust payment terms if needed
- Set due date based on customer agreement
- Add any additional charges (delivery, installation, etc.)

#### Step 5: Add Discounts (If Applicable)
- If customer is eligible for discount:
  - Add discount percentage or amount
  - System recalculates grand total
  - **Note**: Discounts in Payment Entry require Manager approval

#### Step 6: Save as Draft
- Click **Save** to save as Draft
- Can make further edits if needed
- Review invoice before submission

#### Step 7: Submit Sales Invoice
- Click **Submit** button
- Invoice is submitted and posted to accounts
- **Customer notification is triggered automatically**
- Status changes to "Unpaid" (if not paid immediately)
- **Chart of Accounts is updated automatically**:
  - Debit: Accounts Receivable (Customer account)
  - Credit: Sales Account (Revenue account)
  - Tax accounts updated based on tax template

---

## Customer Notification on Sales Invoice Creation

### Notification Trigger

When a Sales Invoice is **created and submitted**, the system must automatically send a notification to the customer via **Email and WhatsApp**.

### Implementation Approach

We will use **Frappe's Document Events Hook** to trigger the notification when the Sales Invoice is submitted.

### Function Declaration

#### File Location
```
fabric_sense/fabric_sense/py/sales_invoice.py
```

#### Function Name
```python
send_customer_invoice_notification
```

#### Function Purpose
This function will:
1. Detect when a Sales Invoice is submitted
2. Retrieve customer contact details (email, phone number)
3. Prepare notification content with invoice details
4. Send Email notification using Frappe's email API
5. Send WhatsApp notification using WhatsApp Business API
6. Update the Sales Invoice to mark notification as sent
7. Log notification status for tracking

#### Function Signature
```python
def send_customer_invoice_notification(doc, method=None):
    """
    Send email and WhatsApp notification to customer when Sales Invoice is created.
    
    Args:
        doc (Document): Sales Invoice document object
        method (str): Event method name (e.g., 'on_submit')
    
    Returns:
        None
    
    Raises:
        Exception: If notification sending fails
    """
```

### Registering the Hook

**File**: `fabric_sense/fabric_sense/hooks.py`

```python
doc_events = {
    "Sales Invoice": {
        "on_submit": "fabric_sense.fabric_sense.py.sales_invoice.send_customer_invoice_notification",
    }
}
```

### Notification Content Templates

#### Email Template

**Subject:** Invoice {invoice_number} - Fabric Sense

**Body:**
```
Dear {customer_name},

Your order invoice has been generated and is ready for payment.

Invoice Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Invoice Number: {invoice_number}
Invoice Date: {invoice_date}
Due Date: {due_date}
Total Amount: ₹{grand_total}
Outstanding Amount: ₹{outstanding_amount}

Items Invoiced:
{item_list}

Payment Terms:
{payment_terms}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Payment Methods:
💳 Bank Transfer
💰 Cash
📱 UPI/Digital Payment

Bank Details:
{bank_details}

You can view and download your invoice online at:
{invoice_url}

If you have any questions, please contact us at:
📞 {company_phone}
📧 {company_email}

Thank you for your business!

Best regards,
Fabric Sense Team
```

#### WhatsApp Template

```
📄 *Invoice Generated!*

Dear {customer_name},

Your invoice is ready! 💼

*Invoice Details:*
• Invoice No: {invoice_number}
• Date: {invoice_date}
• Due Date: {due_date}
• Amount: ₹{grand_total}

*Payment Options:*
💳 Bank Transfer
💰 Cash
📱 UPI

View Invoice: {short_url}

Thank you! 🙏
*Fabric Sense*
```

---

## Order Ready Notification

### When to Send Order Ready Notification

The Order Ready Notification should be sent when:
- All items in the Sales Order are ready for delivery
- For raw material orders: Items are in stock and packed
- For stitched curtains: Tailoring is completed and quality checked
- Before creating the Delivery Note

### Implementation Approach

#### Manual Trigger Option

Add a custom button on the Sales Invoice form to manually trigger the order ready notification.

**File**: `fabric_sense/fabric_sense/public/js/sales_invoice.js`

```javascript
frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        // Show "Send Order Ready Notification" button
        if (frm.doc.docstatus === 1 && !frm.doc.order_ready_notification_sent) {
            frm.add_custom_button(__('Send Order Ready Notification'), function() {
                frappe.call({
                    method: 'fabric_sense.fabric_sense.py.sales_invoice_notifications.send_order_ready_notification',
                    args: {
                        sales_invoice_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__('Order Ready Notification sent successfully'));
                            frm.reload_doc();
                        }
                    }
                });
            }, __('Notifications'));
        }
    }
});
```

#### Function Declaration

**File**: `fabric_sense/fabric_sense/py/sales_invoice.py`

```python
def send_order_ready_notification(sales_invoice_name):
    """
    Send order ready notification to customer.
    
    Args:
        sales_invoice_name (str): Name of the Sales Invoice
    
    Returns:
        dict: Success status and message
    """
```

### Order Ready Notification Templates

#### Email Template

**Subject:** Your Order is Ready for Delivery - Fabric Sense

**Body:**
```
Dear {customer_name},

Great news! Your order is now ready for delivery! 🎉

Order Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order Number: {order_number}
Invoice Number: {invoice_number}
Order Date: {order_date}
Ready Date: {ready_date}

Items Ready:
{item_list}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
1. Complete payment if not already done
2. Schedule delivery/pickup
3. Prepare delivery location

Delivery Options:
🚚 Home Delivery
🏪 Showroom Pickup

Please contact us to schedule delivery:
📞 {company_phone}
📧 {company_email}

We look forward to delivering your order!

Best regards,
Fabric Sense Team
```

#### WhatsApp Template

```
🎉 *Order Ready!*

Dear {customer_name},

Your order is ready for delivery! ✅

*Order Details:*
• Order No: {order_number}
• Invoice No: {invoice_number}
• Ready Date: {ready_date}

*Next Steps:*
✓ Complete payment
✓ Schedule delivery

Contact us to arrange delivery:
📞 {company_phone}

Thank you! 🙏
*Fabric Sense*
```

---

## Delivery Note Creation

### Prerequisites

A Delivery Note can **only** be created when:

1. **Sales Invoice is Submitted**
   - Invoice has been created and submitted
   - Customer has been notified
   - Payment is received or scheduled

2. **Items Ready for Delivery**
   - All items are available in warehouse
   - Items are packed and quality checked
   - For stitched orders: Tailoring is completed

3. **Delivery Details Confirmed**
   - Delivery address is verified
   - Delivery date is scheduled
   - Customer is ready to receive

---

## Using Default Delivery Note Doctype

ERPNext's standard **Delivery Note** doctype provides comprehensive functionality for delivery management:

### Standard Features Available

- **Delivery Management**: Track goods delivered to customers
- **Item Details**: Multiple items with quantities and batch/serial numbers
- **Stock Update**: Automatic stock reduction on submission
- **Packing Slip**: Generate packing slips for shipments
- **Transporter Details**: Record transporter and vehicle information
- **Status Tracking**: Draft, Submitted, Completed, Cancelled
- **Document Links**: Links to Sales Orders, Sales Invoices
- **Print Formats**: Professional delivery note templates

### Standard Fields Used

| Field Name | Field Type | Description | Usage in Fabric Sense |
|------------|-----------|-------------|----------------------|
| `customer` | Link (Customer) | Customer reference | Auto-populated from Sales Order |
| `posting_date` | Date | Delivery date | Date when delivery is made |
| `items` | Table | Delivery items | Auto-populated from Sales Order/Invoice |
| `shipping_address` | Link | Delivery address | Customer's delivery location |
| `status` | Select | Delivery status | System-controlled |
| `sales_invoice` | Link | Reference to Sales Invoice | Links to invoice |
| `sales_order` | Link | Reference to Sales Order | Links to originating SO |

---

## Creating Delivery Note from Sales Order/Invoice

### User Journey - Salesperson

#### Step 1: Open Sales Order or Sales Invoice
- Navigate to the Sales Order or Sales Invoice
- Verify all items are ready for delivery
- Check if payment is received (if required before delivery)
- Confirm delivery address and schedule

#### Step 2: Click "Create Delivery Note" Button
- ERPNext provides a standard "Create" button
- Select "Delivery Note" from the dropdown
- System opens new Delivery Note form

#### Step 3: Delivery Note Auto-Population
- System creates a new Delivery Note with:
  - Customer details from Sales Order/Invoice
  - All items from Sales Order/Invoice
  - Quantities pre-filled
  - Delivery address populated
  - Sales Order/Invoice reference linked

#### Step 4: Review and Adjust
- Salesperson reviews the auto-populated data
- Verify item quantities to be delivered
- Check delivery address
- Add delivery instructions if needed
- Set actual delivery date
- Add transporter details (if applicable)

#### Step 5: Handle Partial Deliveries (If Applicable)
- If delivering only some items:
  - Adjust quantities for items being delivered
  - Remaining items will be in pending delivery
  - Can create multiple Delivery Notes for same order

#### Step 6: Save as Draft
- Click **Save** to save as Draft
- Can make further edits if needed
- Review delivery note before submission

#### Step 7: Submit Delivery Note
- Click **Submit** button
- Delivery Note is submitted
- **Stock is automatically updated**:
  - Items are deducted from warehouse
  - Stock levels are reduced
  - Stock ledger is updated
- **Customer notification is triggered automatically**
- Status changes to "Completed"

---

## Stock Update on Delivery Note Submission

### Automatic Stock Update

When a Delivery Note is submitted, ERPNext automatically:

1. **Reduces Stock Quantity**
   - Items are deducted from the source warehouse
   - Stock balance is updated in real-time
   - Stock ledger entries are created

2. **Updates Material Request Status**
   - Linked Material Requests are marked as "Issued"
   - Fulfillment status is updated

3. **Updates Sales Order Status**
   - Delivery status is updated
   - If all items delivered, Sales Order status becomes "Completed"


### Important Note for Stitched Curtains

For stitched curtain orders (Case II):
- Stock for tailoring materials is already updated when tailoring job starts
- Delivery Note should only update stock for items **not consumed during tailoring**
- Items like accessories, additional materials, etc. that were not part of tailoring

---

## Customer Notification on Delivery Note Creation

### Notification Trigger

When a Delivery Note is **created and submitted**, the system must automatically send a notification to the customer via **Email and WhatsApp**.

### Implementation Approach

We will use **Frappe's Document Events Hook** to trigger the notification when the Delivery Note is submitted.

### Function Declaration

#### File Location
```
fabric_sense/fabric_sense/py/delivery_note.py
```

#### Function Name
```python
send_customer_delivery_notification
```

#### Function Purpose
This function will:
1. Detect when a Delivery Note is submitted
2. Retrieve customer contact details (email, phone number)
3. Prepare notification content with delivery details
4. Send Email notification using Frappe's email API
5. Send WhatsApp notification using WhatsApp Business API
6. Update the Delivery Note to mark notification as sent
7. Log notification status for tracking

#### Function Signature
```python
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
```

### Registering the Hook

**File**: `fabric_sense/fabric_sense/hooks.py`

```python
doc_events = {
    "Delivery Note": {
        "on_submit": "fabric_sense.fabric_sense.py.delivery_note.send_customer_delivery_notification",
    }
}
```

### Notification Content Templates

#### Email Template

**Subject:** Your Order Has Been Delivered - Fabric Sense

**Body:**
```
Dear {customer_name},

Your order has been successfully delivered! 📦

Delivery Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Delivery Note Number: {delivery_note_number}
Delivery Date: {delivery_date}
Order Number: {order_number}
Invoice Number: {invoice_number}

Items Delivered:
{item_list}

Delivered To:
{delivery_address}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please verify the items received and their condition.

If you notice any issues or have concerns, please contact us immediately:
📞 {company_phone}
📧 {company_email}

You can view your delivery note online at:
{delivery_note_url}

Thank you for choosing Fabric Sense!
We hope you enjoy your purchase! 😊

Best regards,
Fabric Sense Team
```

#### WhatsApp Template

```
📦 *Order Delivered!*

Dear {customer_name},

Your order has been delivered successfully! ✅

*Delivery Details:*
• Delivery Note: {delivery_note_number}
• Date: {delivery_date}
• Order No: {order_number}

*Items Delivered:*
{item_list_short}

Please verify items received.

Any issues? Contact us:
📞 {company_phone}

View Delivery Note: {short_url}

Thank you for choosing us! 🙏
*Fabric Sense*
```

---

## Complete Workflow Summary

### Case I: Raw Material Sales

```
1. Sales Order Approved
   ↓
2. Material Request Created & Processed
   ↓
3. Sales Invoice Created → Customer Notification Sent
   ↓
4. Order Ready → Order Ready Notification Sent
   ↓
5. Delivery Note Created → Stock Updated → Customer Notification Sent
   ↓
6. Payment Entry (covered in separate document)
```

### Case II: Stitched Curtains

```
1. Sales Order Approved
   ↓
2. Tailoring Sheet Created
   ↓
3. Material Request Created & Processed
   ↓
4. Tailoring Job Started → Stock Updated
   ↓
5. Tailoring Job Completed
   ↓
6. Sales Invoice Created → Customer Notification Sent
   ↓
7. Order Ready → Order Ready Notification Sent
   ↓
8. Delivery Note Created → Stock Updated (for non-tailoring items) → Customer Notification Sent
   ↓
9. Payment Entry (covered in separate document)
```

---

## Notification Implementation Summary

### Required Notification Functions

Create the following Python files in `fabric_sense/fabric_sense/py/`:

1. **sales_invoice_notifications.py**
   - `send_customer_invoice_notification(doc, method=None)`
   - `send_order_ready_notification(sales_invoice_name)`

2. **delivery_note_notifications.py**
   - `send_customer_delivery_notification(doc, method=None)`

### Hook Registration

Add to `fabric_sense/fabric_sense/hooks.py`:

```python
doc_events = {
    "Sales Invoice": {
        "on_submit": "fabric_sense.fabric_sense.py.sales_invoice_notifications.send_customer_invoice_notification",
    },
    "Delivery Note": {
        "on_submit": "fabric_sense.fabric_sense.py.delivery_note_notifications.send_customer_delivery_notification",
    }
}
```

### Implemented Notification Logic (current code)

- **Sales Invoice notifications** (`fabric_sense/fabric_sense/py/sales_invoice_notifications.py`)
  - Triggered on submit only; exits quietly if docstatus ≠ 1.
  - Resolves customer email in order: invoice contact → linked Contact → Dynamic Link Contact → Customer master.
  - Builds rich HTML invoice email with item table, totals, payment status badge, due date text, and invoice URL.
  - Sends immediately via `frappe.sendmail`; shows success alert; logs success/error without blocking submission.

- **Purchase Order vendor notifications** (`fabric_sense/fabric_sense/py/purchase_order_notifications.py`)
  - Triggered on submit only; exits if docstatus ≠ 1.
  - Finds vendor email from PO contact, Supplier Contact, or Dynamic Link.
  - Sends HTML PO summary (items, amounts, delivery address, payment terms, PO link).
  - Uses `frappe.sendmail`; warns if email missing; logs success/error.

- **Payment Entry customer notifications** (`fabric_sense/fabric_sense/py/payment_entry_notifications.py`)
  - Triggered on submit but only for incoming customer payments (`payment_type == "Receive"` and `party_type == "Customer"`).
  - Resolves customer email with same cascade as Sales Invoice.
  - Builds receipt email with payment details, reference info, allocation table to Sales Invoices (showing outstanding status badges), and payment URL.
  - Sends via `frappe.sendmail`; logs success/error; alerts user when sent or when no email found.

### Unit Test Coverage (notification flows)

- **Location**: `fabric_sense/fabric_sense/py/test_notifications.py`
- **Sales Invoice**: skips when docstatus is not submitted; asserts no send when customer email is missing; happy path covers sending for a submitted invoice with a reachable email.
- **Purchase Order**: skips when docstatus is not submitted; asserts no send when vendor email is missing; happy path covers sending for a submitted PO with vendor email.
- **Payment Entry**: skips when `payment_type` is not Receive or `party_type` is not Customer; asserts no send when customer email is missing; happy path covers incoming customer payments and verifies allocations are included.
- **How to run (CLI)**:
  1) From bench root, activate env if needed: `source ../env/bin/activate`
  2) `cd apps/fabric_sense`
  3) Run tests: `bench --site <yoursite> run-tests --module fabric_sense.fabric_sense.py.test_notifications`
  4) Expect 0 failures and the documented skips
  5) `deactivate` (optional)

---

## Next Steps

After implementing Sales Invoice and Delivery Note creation:
1. Implement Payment Entry workflow with discount approval
2. Set up Manager approval for payment entries
3. Configure discount approval workflow
4. Implement payment reconciliation
5. Set up payment notifications

---

## Reference Documents

- [Sales Order Creation Guide](./sales_order_creation.md)
- [Material Request Creation Guide](./material_request_creation.md)
- [Measurement Sheet Creation Guide](./measurement_sheet_creation.md)
- [Lead, Customer, and Project Creation](./lead_customer_project_creation.md)
- [Case I Implementation](../case-i-implementation.md)
- [Case II Implementation](../case-ii-implementation.md)
- [Overview](../overview.md)

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Author**: Fabric Sense Development Team
