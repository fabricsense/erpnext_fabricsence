# Sales Order Creation Guidelines

## Overview

This guide covers the creation and workflow management of Sales Orders in the Fabric Sense application. Sales Orders are created from approved Measurement Sheets and require Manager approval before proceeding with material requests and fulfillment. We utilize ERPNext's default Sales Order doctype with customizations and workflow enhancements.

---

## Sales Order Creation Prerequisites

### Mandatory Conditions

A Sales Order can **only** be created when:

1. **Measurement Sheet Status = "Approved"**
   - The Measurement Sheet must be in the "Approved" state
   - Customer has reviewed and confirmed the measurements
   - All pricing and quantities are finalized

2. **Customer Record Exists**
   - A valid Customer record must be linked to the Measurement Sheet
   - Customer billing and shipping addresses should be configured

3. **Items Available in Item Master**
   - All fabric types, accessories, and materials must exist in the Item Master
   - Items should have valid SKUs in the format: `CATEGORY-VENDOR-RUNNINGNUMBER`
   - Price Lists should be configured for the customer's Customer Group

---

## Using Default Sales Order Doctype

ERPNext's standard **Sales Order** doctype provides comprehensive functionality for managing customer orders:

### Standard Features Available

- **Order Management**: Track customer orders from creation to delivery
- **Item Details**: Multiple items with quantities, rates, and amounts
- **Pricing**: Automatic price fetching from Price Lists based on Customer Group
- **Taxes and Charges**: Apply tax templates and additional charges
- **Delivery Date**: Track expected delivery dates
- **Payment Terms**: Configure payment schedules
- **Status Tracking**: Draft, Submitted, Approved, Completed, Cancelled
- **Document Links**: Links to Quotations, Material Requests, Sales Invoices, Delivery Notes

### Standard Fields Used

| Field Name | Field Type | Description | Usage in Fabric Sense |
|------------|-----------|-------------|----------------------|
| `customer` | Link (Customer) | Customer reference | Auto-populated from Measurement Sheet |
| `transaction_date` | Date | Order date | Date when Sales Order is created |
| `delivery_date` | Date | Expected delivery | Calculated based on lead time |
| `items` | Table | Order items | Auto-populated from Measurement Sheet |
| `total` | Currency | Total amount | Auto-calculated |
| `grand_total` | Currency | Final amount with taxes | Auto-calculated |
| `status` | Select | Order status | Workflow-controlled |

---

## Customizing Sales Order Doctype

To meet Fabric Sense specific requirements, we need to add custom fields and modify properties.

### Steps to Customize Sales Order

1. **Open Customize Form**
   - Navigate to **Sales Order List**
   - Click **Menu** (three dots) → **Customize**

2. **Add Custom Fields**
   - Click **Add Row** in the Fields table
   - Add each custom field as specified above
   - Configure field properties (Label, Type, Options, Mandatory, etc.)
   - Position fields appropriately in the form layout

3. **Modify Existing Field Properties** (if needed)
   - Make certain fields mandatory/read-only based on workflow
   - Add field dependencies (e.g., show `project` only when `order_type` = "Stitched Curtains")

4. **Save Customizations**
   - Click **Update** to save changes

5. **Export Customizations**
   - Click **Actions** → **Export Customizations**
   - Select module: `fabric_sense`
   - Click **Submit**
   - Customizations will be saved to: `fabric_sense/fabric_sense/custom/sales_order.json`

---

## Sales Order Workflow Implementation

### Workflow States

The Sales Order workflow includes the following states:

1. **Draft**
   - Initial state when Sales Order is created
   - Salesperson can edit the order
   - Not yet submitted for approval

2. **Pending Approval**
   - Sales Order has been submitted by Salesperson
   - Awaiting Manager review and approval
   - Read-only for Salesperson

3. **Approved**
   - Manager has approved the Sales Order
   - Customer notification triggered
   - Ready for Material Request creation
   - Read-only for Salesperson

4. **Rejected**
   - Manager has rejected the Sales Order
   - Salesperson can view rejection reason
   - Can be amended and resubmitted

5. **Completed**
   - All deliveries and invoices are completed
   - Final state

6. **Cancelled**
   - Order has been cancelled
   - Stock reservations released

### Workflow Transitions

```
Draft → Pending Approval (Submit by Salesperson)
Pending Approval → Approved (Approve by Manager)
Pending Approval → Rejected (Reject by Manager)
Rejected → Draft (Amend by Salesperson)
Approved → Completed (Automatic when all deliveries done)
Any State → Cancelled (Cancel by Manager)
```

### Creating the Workflow

1. **Navigate to Workflow**
   - Go to **Setup** → **Workflow** → **Workflow**
   - Click **New**

2. **Configure Workflow**
   - **Document Type**: Sales Order
   - **Workflow Name**: Sales Order Approval Workflow
   - **Is Active**: Yes
   - **Override Status**: Yes (to use custom workflow states)

3. **Add Workflow States**

| State | Doc Status | Allow Edit | Style |
|-------|-----------|-----------|-------|
| Draft | 0 (Draft) | Salesperson, Manager | Primary |
| Pending Approval | 1 (Submitted) | Manager | Warning |
| Approved | 1 (Submitted) | Manager | Success |
| Rejected | 2 (Cancelled) | Salesperson, Manager | Danger |
| Completed | 1 (Submitted) | - | Success |
| Cancelled | 2 (Cancelled) | - | Danger |

4. **Add Workflow Transitions**

| From State | To State | Action | Allowed Role | Condition |
|-----------|---------|--------|--------------|-----------|
| Draft | Pending Approval | Submit for Approval | Salesperson | - |
| Pending Approval | Approved | Approve | Manager | - |
| Pending Approval | Rejected | Reject | Manager | - |
| Rejected | Draft | Revise | Salesperson | - |
| Approved | Completed | Complete | System | All deliveries done |
| Any | Cancelled | Cancel | Manager | - |

5. **Save Workflow**
   - Click **Save**
   - The workflow is now active for all Sales Orders

### Workflow Permissions

Configure role-based permissions:

#### Salesperson Permissions
- Create new Sales Order
- Edit Draft Sales Order
- Submit for Approval (transition to Pending Approval)
- View all states
- Cannot approve or reject

#### Manager Permissions
- All Salesperson permissions
- Approve Sales Order (transition to Approved)
- Reject Sales Order (transition to Rejected)
- Cancel Sales Order
- Override all restrictions

---

## Creating Sales Order from Measurement Sheet

### User Journey - Salesperson

1. **Navigate to Approved Measurement Sheet**
   - Open the Measurement Sheet in "Approved" status
   - Review all measurements and pricing

2. **Click "Create Sales Order" Button**
   - A custom button "Create Sales Order" should be available
   - This button is only visible when status = "Approved"

3. **Sales Order Auto-Population**
   - System creates a new Sales Order with:
     - Customer details from Measurement Sheet
     - All items from Measurement Sheet's measurement_details table
     - Quantities and rates pre-filled
     - Total amounts calculated
     - Measurement Sheet reference linked

4. **Review and Adjust**
   - Salesperson reviews the auto-populated data
   - Can add additional items if needed
   - Adjust delivery dates
   - Add special instructions in notes

5. **Save as Draft**
   - Click **Save** to save as Draft
   - Can make further edits if needed

6. **Submit for Approval**
   - Click **Submit** button
   - Workflow transitions to "Pending Approval"
   - Manager receives notification (optional)

### User Journey - Manager

1. **Review Sales Order**
   - Open the Sales Order
   - Review customer details, items, quantities, pricing
   - Check Measurement Sheet reference
   - Verify calculations and totals

3. **Approve or Reject**
   - **If Approved**:
     - Click **Approve** button
     - Workflow transitions to "Approved"
     - `approval_status` = "Approved"
     - `approved_by` = Current Manager
     - `approval_date` = Current timestamp
     - **Customer notification is triggered automatically**
   
   - **If Rejected**:
     - Click **Reject** button
     - Enter `rejection_reason` in the dialog
     - Workflow transitions to "Rejected"
     - Salesperson can view reason and revise

---

## Customer Notification on Approval

### Notification Trigger

When a Sales Order is **approved by the Manager**, the system must automatically send a notification to the customer via **Email and WhatsApp**.

### Implementation Approach

We will use **Frappe's Document Events Hook** to trigger the notification when the Sales Order status changes to "Approved".

### Function Declaration

#### File Location
```
fabric_sense/fabric_sense/doctype/sales_order/sales_order_notifications.py
```

#### Function Name
```python
send_customer_approval_notification
```

#### Function Purpose
This function will:
1. Detect when a Sales Order is approved (status changes to "Approved")
2. Retrieve customer contact details (email, phone number)
3. Prepare notification content with order details
4. Send Email notification using Frappe's email API
5. Send WhatsApp notification using WhatsApp Business API
6. Update the Sales Order to mark notification as sent
7. Log notification status for tracking

#### Function Signature
```python
def send_customer_approval_notification(doc, method=None):
    """
    Send email and WhatsApp notification to customer when Sales Order is approved.
    
    Args:
        doc (Document): Sales Order document object
        method (str): Event method name (e.g., 'on_update', 'on_submit')
    
    Returns:
        None
    
    Raises:
        Exception: If notification sending fails
    """
```

### Registering the Hook

To trigger the notification function when a Sales Order is updated, we need to register it in the `hooks.py` file.

#### File Location
```
fabric_sense/fabric_sense/hooks.py
```

#### Hook Configuration

Add the following to the `doc_events` section in `hooks.py`:

```python
doc_events = {
    "Sales Order": {
        "on_update": "fabric_sense.fabric_sense.doctype.sales_order.sales_order_notifications.send_customer_approval_notification",
    }
}
```

**Explanation:**
- **`on_update`**: Triggers when the Sales Order is updated (including status changes)
- The function checks if `approval_status == "Approved"` and `customer_notification_sent == False` before sending

### Alternative: Using Workflow Action

Instead of document events, you can also trigger the notification directly from the Workflow Action.

#### Steps:

1. **Edit Workflow Transition**
   - Open the Sales Order Approval Workflow
   - Find the transition: "Pending Approval" → "Approved"

2. **Add Action**
   - In the transition row, add a custom action
   - Action: `send_customer_approval_notification`
   - This will execute the function when the transition occurs

3. **Configure Action in Workflow**
   - Workflow Actions can call server-side methods
   - Specify the method path: `fabric_sense.fabric_sense.doctype.sales_order.sales_order_notifications.send_customer_approval_notification`

---

## Notification Content Templates

### Email Template

**Subject:** Sales Order {order_number} Approved - Fabric Sense

**Body:**
```
Dear {customer_name},

We are pleased to inform you that your Sales Order has been approved and is now being processed.

Order Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order Number: {order_number}
Order Date: {order_date}
Expected Delivery: {delivery_date}
Total Amount: {grand_total}

Items Ordered:
{item_list}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
1. Material procurement is in progress
2. You will receive updates on order preparation
3. Delivery notification will be sent when ready

You can track your order status online at:
{order_url}

If you have any questions, please contact us at:
📞 {company_phone}
📧 {company_email}

Thank you for choosing Fabric Sense!

Best regards,
Fabric Sense Team
```

### WhatsApp Template

```
🎉 *Order Approved!*

Dear {customer_name},

Your order *{order_number}* has been approved! ✅

📦 *Order Details:*
• Order No: {order_number}
• Date: {order_date}
• Delivery: {delivery_date}
• Amount: ₹{grand_total}

We're now processing your order. You'll receive updates soon!

Track your order: {short_url}

Thank you! 🙏
*Fabric Sense*
```

---

## Additional Scenarios

### Handling Additional Items in Sales Order

#### Scenario 1: Customer Requests Additional Items

**Process:**
1. Salesperson opens the existing Sales Order
2. Adds new items to the items table
3. Saves the Sales Order (triggers recalculation)
4. Creates a new Material Request for the additional items
5. Material Request requires Manager approval before submission
6. After approval, stock is reserved/purchased

**Implementation Notes:**
- Track which items are "additional" using a custom field `is_additional_item` in Sales Order Item table
- Material Requests created for additional items should be flagged for Manager approval
- Workflow should prevent submission of Material Request until Manager approves

#### Scenario 2: Damaged Item Replacement

**Process:**
1. Salesperson identifies damaged item
2. Creates a Material Request (Issue) for replacement
3. **Does NOT update the Sales Order** (no new items added)
4. Material Request references the original Sales Order
5. Material Request requires Manager approval
6. After approval, stock is issued for replacement
7. No additional invoice or payment required

**Implementation Notes:**
- Add custom field `is_replacement` in Material Request
- Replacement Material Requests should not create new Sales Invoice items
- Track replacement history for reporting

---

## Sales Order Item Table Auto-Population

### Mapping from Measurement Sheet to Sales Order

When creating a Sales Order from an approved Measurement Sheet, the system should automatically populate the items table with all items from the Measurement Sheet.

#### Mapping Logic

| Measurement Sheet Field | Sales Order Item Field | Notes |
|------------------------|----------------------|-------|
| `fabric_type` | `item_code` | Main fabric item |
| `quantity` | `qty` | Calculated fabric quantity |
| `rate` | `rate` | Price from Price List |
| `amount` | `amount` | Auto-calculated (qty × rate) |
| `lead_rope` | `item_code` | Additional row for lead rope |
| `lining` | `item_code` | Additional row for lining |
| `track_rod_type` | `item_code` | Additional row for track/rod |

#### Implementation Approach

Create a server-side method to handle the mapping:

**File:** `fabric_sense/fabric_sense/doctype/measurement_sheet/measurement_sheet.py`

```

#### Adding "Create Sales Order" Button

Add a custom button to the Measurement Sheet form:

**File:** `fabric_sense/fabric_sense/doctype/measurement_sheet/measurement_sheet.js`

```javascript
frappe.ui.form.on('Measurement Sheet', {
    refresh: function(frm) {
        // Show "Create Sales Order" button only when status is Approved
        if (frm.doc.status === "Approved" && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create Sales Order'), function() {
                frappe.call({
                    method: 'fabric_sense.fabric_sense.doctype.measurement_sheet.measurement_sheet.create_sales_order_from_measurement_sheet',
                    args: {
                        measurement_sheet_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__('Sales Order {0} created successfully', [r.message.name]));
                            frappe.set_route('Form', 'Sales Order', r.message.name);
                        }
                    }
                });
            }, __('Create'));
        }
    }
});
```

---

### Next Steps

After implementing Sales Order creation:
1. Proceed with Material Request creation from Sales Order
2. Implement Purchase Order workflow for on-order items
3. Configure Sales Invoice and Delivery Note creation
4. Set up Payment Entry workflow with discount approval

---

## Reference Documents

- [Measurement Sheet Creation Guide](./measurement_sheet_creation.md)
- [Lead, Customer, and Project Creation](./lead_customer_project_creation.md)
- [Case I Implementation](../case-i-implementation.md)
- [Case II Implementation](../case-ii-implementation.md)
- [Overview](../overview.md)

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Author**: Fabric Sense Development Team
