# Material Request Creation Guidelines

## Overview

This guide covers the creation and workflow management of Material Requests in the Fabric Sense application. Material Requests are created corresponding to approved Sales Orders and are used to reserve in-stock items or initiate purchase orders for on-order items. We utilize ERPNext's default Material Request doctype with customizations and workflow enhancements to ensure proper stock management and Manager approval for multiple requests.

---

## Material Request Creation Prerequisites

### Mandatory Conditions

A Material Request can **only** be created when:

1. **Sales Order Status = "Approved"**
   - The Sales Order must be in the "Approved" state
   - Manager has reviewed and approved the order
   - Customer notification has been sent

2. **Sales Order Items Available**
   - Sales Order must contain at least one item
   - Item quantities must be specified
   - Items must exist in the Item Master

3. **Warehouse Configuration**
   - Default warehouse must be configured
   - Warehouse must be active and accessible
   - Stock levels must be trackable

---

## Using Default Material Request Doctype

ERPNext's standard **Material Request** doctype provides comprehensive functionality for managing material requirements:

### Standard Features Available

- **Material Request Types**: Issue, Purchase, Transfer, Manufacture
- **Item Management**: Multiple items with quantities and required dates
- **Stock Availability Check**: Real-time stock level verification
- **Purchase Order Creation**: Direct conversion to Purchase Order
- **Approval Workflow**: Multi-level approval support
- **Status Tracking**: Draft, Submitted, Ordered, Issued, Cancelled
- **Document Links**: Links to Sales Orders, Purchase Orders, Stock Entries

### Standard Fields Used

| Field Name | Field Type | Description | Usage in Fabric Sense |
|------------|-----------|-------------|----------------------|
| `naming_series` | Data | Auto-naming (MR-.YYYY.-) | Default ERPNext naming |
| `material_request_type` | Select | Issue/Purchase | Issue for in-stock, Purchase for on-order |
| `transaction_date` | Date | Request date | Date when MR is created |
| `schedule_date` | Date | Required by date | Expected delivery/issue date |
| `items` | Table | Material request items | Items from Sales Order |
| `status` | Select | Request status | Workflow-controlled |
| `sales_order` | Link | Reference to Sales Order | Links to originating SO |

---


## Material Request Types

### 1. Issue Purpose (In-Stock Items)

**Purpose**: Reserve materials that are already available in the warehouse.

**When to Use**:
- Items are available in sufficient quantity in stock
- No purchase is required
- Immediate reservation is needed

**Process**:
1. Check stock availability before creating
2. Create Material Request with type = "Issue"
3. System validates stock levels
4. If stock insufficient, show error message
5. If stock available, reserve items
6. Create Stock Entry to issue materials

**Stock Availability Validation**:
```python
# Pseudo-code for stock check
for item in material_request.items:
    available_qty = get_stock_qty(item.item_code, warehouse)
    if available_qty < item.qty:
        frappe.throw(f"Insufficient stock for {item.item_code}. Available: {available_qty}, Required: {item.qty}")
```

### 2. Purchase Purpose (On-Order Items)

**Purpose**: Initiate purchase for items that need to be ordered from suppliers.

**When to Use**:
- Items are not available in stock
- Items need to be purchased from vendor
- Lead time is acceptable for delivery

**Process**:
1. Create Material Request with type = "Purchase"
2. No stock validation required
3. System creates link to Sales Order
4. Purchase Order can be created from this MR
5. Vendor notification sent after PO creation
6. Stock updated when items are received

---

## Material Request Creation Workflow

### Scenario 1: First Material Request for Sales Order

This is the standard flow when creating the first Material Request for a Sales Order.

**Process**:
1. Salesperson opens approved Sales Order
2. Clicks "Create Material Request" button
3. System checks if any MR already exists for this SO
4. If first MR, proceed without Manager approval
5. Salesperson selects Material Request Type (Issue/Purchase)
6. Items auto-populate from Sales Order
7. Salesperson reviews and submits
8. MR is created and processed

**No Manager Approval Required** for first Material Request.

### Scenario 2: Additional Material Request for Same Sales Order

When more than one Material Request needs to be created for the same Sales Order, Manager approval is mandatory.

**Trigger Conditions**:
- Customer requests additional items/quantities
- Initial material request was insufficient
- Additional fabric needed due to measurement adjustments

**Process**:
1. Salesperson creates new Material Request
2. Links to existing Sales Order
3. System detects existing MR for this SO
4. Automatically sets `is_additional_request` = True
5. Automatically sets `requires_manager_approval` = True
6. Salesperson enters `additional_request_reason`
7. Salesperson saves as Draft
8. Salesperson submits for Manager approval
9. Manager reviews and approves/rejects
10. If approved, MR can be processed
11. If rejected, Salesperson can revise

**Manager Approval Required** for additional Material Requests.

### Scenario 3: Replacement Material Request (Damaged Items)

When items are damaged and need replacement without updating the Sales Order.

**Trigger Conditions**:
- Item damaged during handling
- Quality issue with delivered item
- Customer reports defective item

**Process**:
1. Salesperson creates new Material Request
2. Links to original Sales Order
3. Sets `is_replacement` = True
4. Enters `replacement_reason`
5. **Does NOT update Sales Order items**
6. System automatically sets `requires_manager_approval` = True
7. Salesperson submits for Manager approval
8. Manager reviews reason and approves/rejects
9. If approved, stock is issued for replacement
10. **No additional invoice or payment required**

**Manager Approval Required** for replacement Material Requests.

---

## Stock Availability Validation for Issue Purpose

### Validation Logic

When creating a Material Request with **Issue Purpose**, the system must validate stock availability before allowing submission.

### Implementation Approach

**Server-side Validation** in Material Request controller:

**File**: `fabric_sense/fabric_sense/py/material_request.py`

```python
def validate_stock_availability(doc, method=None):
    """
    Validate stock availability for Material Request with Issue purpose.
    Show toast message if stock is insufficient.
    """
```

### Registering the Validation Hook

**File**: `fabric_sense/fabric_sense/hooks.py`

```python
doc_events = {
    "Material Request": {
        "validate": "fabric_sense.fabric_sense.custom.material_request.validate_stock_availability",
    }
}
```

## Creating Material Request from Sales Order

### User Journey - Salesperson

#### Step 1: Open Approved Sales Order
- Navigate to approved Sales Order
- Review items and quantities
- Verify customer requirements

#### Step 2: Check Existing Material Requests
- System automatically checks if MRs exist for this SO
- If first MR: Standard flow (no approval needed)
- If additional MR: Approval flow triggered

#### Step 3: Click "Create Material Request" Button
- Custom button available on Sales Order
- Opens Material Request creation form

#### Step 4: Select Material Request Type

**Option A: Issue Purpose (In-Stock Items)**
- Select "Issue" as Material Request Type
- System validates stock availability
- If stock insufficient, error message shown
- If stock available, proceed

**Option B: Purchase Purpose (On-Order Items)**
- Select "Purchase" as Material Request Type
- No stock validation required
- Proceed with MR creation

#### Step 5: Auto-Population of Items
- Items from Sales Order auto-populate
- Quantities pre-filled
- Warehouse pre-selected
- Required date calculated

#### Step 6: Review and Adjust
- Review auto-populated items
- Adjust quantities if needed
- Set schedule dates
- Add notes if necessary

#### Step 7: Handle Additional/Replacement Scenarios

**If Additional Request**:
- System detects existing MR
- Sets `is_additional_request` = True
- Enter `additional_request_reason`
- System sets `requires_manager_approval` = True

**If Replacement Request**:
- Check `is_replacement` checkbox
- Enter `replacement_reason`
- System sets `requires_manager_approval` = True
- **Do not update Sales Order**

#### Step 8: Save and Submit

**If First MR**:
- Click **Save**
- Click **Submit**
- MR is submitted directly
- No Manager approval needed

**If Additional/Replacement MR**:
- Click **Save**
- Click **Submit for Approval**
- MR goes to "Pending Manager Approval"
- Manager receives notification

### User Journey - Manager

#### Step 1: Review Material Request
- Open MR in "Pending Manager Approval" state
- Review linked Sales Order
- Check reason for additional/replacement request
- Verify item quantities and requirements

#### Step 2: Verify Justification

**For Additional Requests**:
- Check `additional_request_reason`
- Verify if customer requested additional items
- Confirm if initial MR was insufficient
- Review cost implications

**For Replacement Requests**:
- Check `replacement_reason`
- Verify if item was genuinely damaged
- Confirm no invoice/payment impact
- Review replacement history

#### Step 3: Approve or Reject

**If Approved**:
- Click **Approve** button
- `manager_approval_status` = "Approved"
- `approved_by_manager` = Current Manager
- `manager_approval_date` = Current timestamp
- MR automatically transitions to "Submitted"
- Can proceed with stock issue/purchase

**If Rejected**:
- Click **Reject** button
- Enter `manager_rejection_reason`
- `manager_approval_status` = "Rejected"
- MR transitions to "Manager Rejected"
- Salesperson can view reason and revise

---

## Purchase Order Creation for On-Order Items

### When to Create Purchase Order

A Purchase Order is created when:
- Material Request Type = "Purchase"
- Items need to be ordered from vendor
- Manager has approved (if additional/replacement MR)

### Process Flow

1. **Material Request Submitted**
   - MR with Purchase Purpose is submitted
   - Status = "Submitted"

2. **Create Purchase Order**
   - Click "Create Purchase Order" button on MR
   - System creates PO with items from MR
   - Pricing fetched from Item Price List

3. **Review Purchase Order**
   - Salesperson reviews PO details
   - Select vendor information
   - Confirms pricing and quantities
   - Adds payment terms if needed

4. **Submit Purchase Order**
   - Click **Submit** on PO
   - PO is sent to vendor
   - **Vendor notification triggered automatically**

5. **Vendor Notification**
   - Email/WhatsApp sent to vendor
   - PO details included
   - Delivery date specified
   - Contact information provided

---

## Vendor Notification on Purchase Order Creation

### Notification Trigger

When a Purchase Order is **created and submitted**, the system must automatically send a notification to the vendor via **Email and WhatsApp**.

### Implementation Approach

We will use **Frappe's Document Events Hook** to trigger the notification when the Purchase Order is submitted.

### Function Declaration

#### File Location
```
fabric_sense/fabric_sense/doctype/purchase_order/purchase_order_notifications.py
```

#### Function Name
```python
send_vendor_po_notification
```

#### Function Purpose
This function will:
1. Detect when a Purchase Order is submitted
2. Retrieve vendor contact details (email, phone number)
3. Prepare notification content with PO details
4. Send Email notification using Frappe's email API
5. Send WhatsApp notification using WhatsApp Business API
6. Update the PO to mark notification as sent
7. Log notification status for tracking

#### Function Signature
```python
def send_vendor_po_notification(doc, method=None):
    """
    Send email and WhatsApp notification to vendor when Purchase Order is submitted.
    
    Args:
        doc (Document): Purchase Order document object
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
    "Purchase Order": {
        "on_submit": "fabric_sense.fabric_sense.py.purchase_order.send_vendor_po_notification",
    }
}
```

### Notification Content Templates

#### Email Template

**Subject:** Purchase Order {po_number} - Fabric Sense

**Body:**
```
Dear {vendor_name},

We are pleased to place the following purchase order with your company.

Purchase Order Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PO Number: {po_number}
PO Date: {po_date}
Required By: {required_date}
Total Amount: {grand_total}

Items Ordered:
{item_list}

Delivery Address:
{delivery_address}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Payment Terms:
{payment_terms}

Please confirm receipt of this order and provide an estimated delivery date.

If you have any questions, please contact us at:
📞 {company_phone}
📧 {company_email}

Thank you for your service!

Best regards,
Fabric Sense Team
```

#### WhatsApp Template

```
📦 *New Purchase Order*

Dear {vendor_name},

We have placed a new order with you! 

*PO Details:*
• PO No: {po_number}
• Date: {po_date}
• Required By: {required_date}
• Amount: ₹{grand_total}

Please confirm receipt and delivery date.

View PO: {short_url}

Thank you! 🙏
*Fabric Sense*
```

---

## Stock Update on Vendor Delivery

### Purchase Receipt Creation

When the vendor delivers the items, stock must be updated using a **Purchase Receipt**.

### Process Flow

1. **Vendor Delivers Items**
   - Vendor delivers items to warehouse
   - Salesperson verifies items against PO
   - Checks quality and quantity

2. **Create Purchase Receipt**
   - Open the Purchase Order
   - Click "Create Purchase Receipt" button
   - Items auto-populate from PO
   - Verify quantities received

3. **Quality Inspection (Optional)**
   - Conduct quality check if required
   - Record inspection results
   - Accept or reject items

4. **Submit Purchase Receipt**
   - Click **Submit** on Purchase Receipt
   - **Stock is automatically updated**
   - Warehouse quantities increase
   - Material Request status updates to "Ordered"

### Stock Update Logic

```python
# Automatic stock update on Purchase Receipt submission
for item in purchase_receipt.items:
    # Increase stock in warehouse
    update_stock(
        item_code=item.item_code,
        warehouse=item.warehouse,
        qty=item.qty,
        voucher_type="Purchase Receipt",
        voucher_no=purchase_receipt.name
    )
    
    # Update Material Request status
    update_material_request_status(
        material_request=item.material_request,
        status="Ordered"
    )
```

---

## Multiple Material Requests - Approval Logic

### Detection Logic

The system automatically detects if a Material Request is additional by checking existing MRs for the same Sales Order.

**Server-side Check**:

```python
def check_if_additional_request(doc, method=None):
    """
    Check if this is an additional Material Request for the same Sales Order.
    Auto-set requires_manager_approval flag.
    """
```

### Approval Enforcement

**Prevent Submission Without Approval**:

```python
def prevent_submission_without_approval(doc, method=None):
    """
    Prevent submission of Material Request if Manager approval is required but not given.
    """
```
---

## Reference Documents

- [Sales Order Creation Guide](./sales_order_creation.md)
- [Measurement Sheet Creation Guide](./measurement_sheet_creation.md)
- [Lead, Customer, and Project Creation](./lead_customer_project_creation.md)
- [Case I Implementation](../case-i-implementation.md)
- [Case II Implementation](../case-ii-implementation.md)
- [Overview](../overview.md)

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Author**: Fabric Sense Development Team
