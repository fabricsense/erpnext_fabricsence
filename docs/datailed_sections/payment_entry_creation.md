# Payment Entry Creation Guidelines

## Overview

This guide covers the creation and workflow management of Payment Entries in the Fabric Sense application. Payment Entries are created against Sales Invoices and require Manager approval before being posted to Accounts. The system supports payments with or without discounts, with additional approval required for discount-based payments. We utilize ERPNext's default Payment Entry doctype with its built-in **"Deductions or Loss"** section for handling discounts, along with minimal custom fields for approval workflow.

---

## Payment Entry Creation Prerequisites

### Mandatory Conditions

A Payment Entry can **only** be created when:

1. **Sales Invoice Exists and is Submitted**
   - A valid Sales Invoice must be created and submitted
   - The invoice should have an outstanding amount > 0
   - Invoice status should not be "Cancelled"

2. **Customer Record is Valid**
   - Customer must have valid contact details
   - Customer billing information should be configured
   - Customer should not be on credit hold

3. **Payment Mode is Configured**
   - Payment modes (Cash, Bank Transfer, Cheque, UPI, etc.) must be set up
   - Bank accounts should be configured for non-cash payments
   - Chart of Accounts should have appropriate payment accounts

---

## Using Default Payment Entry Doctype

ERPNext's standard **Payment Entry** doctype provides comprehensive functionality for managing customer payments:

### Standard Features Available

- **Payment Management**: Track payments from customers against invoices
- **Multiple Payment Modes**: Cash, Bank, Cheque, Credit Card, UPI, etc.
- **Reference Linking**: Link payments to Sales Invoices, Sales Orders
- **Discount Handling**: Apply payment discounts and write-offs
- **Multi-Currency Support**: Handle payments in different currencies
- **Bank Reconciliation**: Match payments with bank statements
- **Status Tracking**: Draft, Submitted, Cancelled
- **Accounting Integration**: Automatic GL Entry creation

### Standard Fields Used

| Field Name | Field Type | Description | Usage in Fabric Sense |
|------------|-----------|-------------|----------------------|
| `payment_type` | Select | Type of payment (Receive, Pay) | Always "Receive" for customer payments |
| `party_type` | Select | Party type (Customer, Supplier) | Always "Customer" |
| `party` | Link (Customer) | Customer reference | Auto-populated from Sales Invoice |
| `posting_date` | Date | Payment date | Date when payment is received |
| `paid_amount` | Currency | Amount paid by customer | Entered by Salesperson |
| `received_amount` | Currency | Amount received | Same as paid_amount for single currency |
| `mode_of_payment` | Link | Payment method | Cash, Bank, UPI, etc. |
| `references` | Table | Invoice references | Links to Sales Invoice(s) |
| `total_allocated_amount` | Currency | Amount allocated to invoices | Auto-calculated |
| `difference_amount` | Currency | Unallocated amount | Should be 0 for full payment |
| `status` | Select | Payment status | Workflow-controlled |
| `deductions` | Table | Payment Deductions or Loss | **Used for discounts** - see below |

---

## Using Built-in "Deductions or Loss" Section for Discounts

### Overview

Instead of adding custom discount fields, we leverage ERPNext's built-in **"Payment Deductions or Loss"** child table. This section is specifically designed to handle deductions like discounts, bank charges, and other payment-related expenses.

### Standard "Deductions or Loss" Table Fields

| Field Name | Field Type | Description | Usage for Discounts |
|------------|-----------|-------------|---------------------|
| `account` | Link (Account) | Expense account | "Discount Allowed" account |
| `cost_center` | Link (Cost Center) | Cost center for tracking | Main cost center or department |
| `amount` | Currency | Deduction amount | Discount amount given to customer |

### Benefits of Using Deductions Section

✅ **No Custom Fields Needed**: Uses standard ERPNext functionality  
✅ **Automatic GL Entries**: System automatically creates proper accounting entries  
✅ **Standard Accounting Flow**: Follows ERPNext best practices  
✅ **Future-Proof**: Compatible with ERPNext updates  
✅ **Multiple Deductions**: Can handle discount + bank charges in same payment  
✅ **Cost Center Tracking**: Track discounts by department or project  

### How Deductions Work

1. **Salesperson adds deduction row**:
   - Select "Discount Allowed" account
   - Enter discount amount
   - Select cost center

2. **System automatically adjusts**:
   - `paid_amount` = Invoice outstanding - Discount amount
   - `total_deductions` = Sum of all deduction rows
   - GL entries created for both payment and discount

3. **Manager approves**:
   - Reviews deduction account and amount
   - Approves or rejects based on discount policy

### Example Scenario

**Invoice Outstanding**: ₹10,000  
**Discount Given**: ₹500  
**Payment Received**: ₹9,500  

**Deductions Table Entry**:
- Account: "Discount Allowed"
- Cost Center: "Main"
- Amount: ₹500

**Resulting GL Entries** (on submission):
| Account | Debit | Credit |
|---------|-------|--------|
| Bank/Cash | ₹9,500 | - |
| Discount Allowed | ₹500 | - |
| Debtors (Accounts Receivable) | - | ₹10,000 |

---

## Customizing Payment Entry Doctype

To meet Fabric Sense specific requirements, we add minimal custom fields for approval workflow and tracking.

### Custom Fields Required

Add the following custom fields to the Payment Entry doctype:

| Field Name | Label | Field Type | Options | Mandatory | Description |
|-----------|-------|-----------|---------|-----------|-------------|
| `has_deductions` | Has Deductions/Discount | Check | - | No | Auto-set when deductions table has entries |
| `deduction_reason` | Deduction/Discount Reason | Small Text | - | No | Reason for applying deductions |
| `deduction_approved_by` | Deduction Approved By | Link | User | No | Manager who approved deductions |
| `deduction_approval_date` | Deduction Approval Date | Datetime | - | No | When deductions were approved |
| `deduction_approval_status` | Deduction Approval Status | Select | Pending\nApproved\nRejected | No | Status of deduction approval |
| `payment_approval_status` | Payment Approval Status | Select | Pending\nApproved\nRejected | No | Status of payment approval |
| `approved_by` | Approved By | Link | User | No | Manager who approved payment |
| `approval_date` | Approval Date | Datetime | - | No | When payment was approved |
| `rejection_reason` | Rejection Reason | Text | - | No | Reason for rejection |
| `customer_notification_sent` | Customer Notification Sent | Check | - | No | Track if notification sent |
| `notification_sent_date` | Notification Sent Date | Datetime | - | No | When notification was sent |

### Field Dependencies and Validations

#### Deduction Fields Visibility
- `deduction_reason` should be visible only when `has_deductions` = 1
- `deduction_approved_by`, `deduction_approval_date` should be visible only when `deduction_approval_status` = "Approved"

#### Mandatory Field Rules
- If `has_deductions` = 1, then `deduction_reason` is mandatory
- If deductions table has entries, then each row must have an account specified
- `rejection_reason` is mandatory when `payment_approval_status` = "Rejected" or `deduction_approval_status` = "Rejected"

### Steps to Customize Payment Entry

1. **Open Customize Form**
   - Navigate to **Payment Entry List**
   - Click **Menu** (three dots) → **Customize**

2. **Add Custom Fields**
   - Click **Add Row** in the Fields table
   - Add each custom field as specified above
   - Configure field properties (Label, Type, Options, Mandatory, etc.)
   - Position fields appropriately in the form layout

3. **Save Customizations**
   - Click **Update** to save changes

4. **Export Customizations**
   - Click **Actions** → **Export Customizations**
   - Select module: `fabric_sense`
   - Click **Submit**
   - Customizations will be saved to: `fabric_sense/fabric_sense/custom/payment_entry.json`

### Setting Up Discount Account

1. **Navigate to Chart of Accounts**
   - Go to **Accounting** → **Chart of Accounts**

2. **Create Discount Account** (if not exists)
   - Under "Expenses" or "Indirect Expenses"
   - Account Name: "Discount Allowed" or "Sales Discount"
   - Account Type: "Expense Account"
   - Click **Save**

3. **Set as Default** (optional)
   - In Payment Entry customization, you can set this as default account in deductions table

---

## Payment Entry Workflow Implementation

### Workflow States

The Payment Entry workflow includes the following states:

1. **Draft**
   - Initial state when Payment Entry is created
   - Salesperson can edit the payment details
   - Not yet submitted for approval

2. **Pending Deduction Approval** (if deductions applied)
   - Payment Entry has deductions in the "Deductions or Loss" table
   - Awaiting Manager approval for deductions
   - Read-only for Salesperson

3. **Deduction Approved** (if deductions applied)
   - Manager has approved the deductions
   - Now awaiting payment approval
   - Read-only for Salesperson

4. **Deduction Rejected** (if deductions applied)
   - Manager has rejected the deductions
   - Salesperson can revise deductions or remove them
   - Can be amended and resubmitted

5. **Pending Payment Approval**
   - Payment Entry submitted for approval
   - Awaiting Manager approval for payment
   - Read-only for Salesperson

6. **Approved**
   - Manager has approved the payment
   - Ready to be posted to Accounts
   - Can now be submitted to create GL Entries

7. **Rejected**
   - Manager has rejected the payment
   - Salesperson can view rejection reason
   - Can be amended and resubmitted

8. **Submitted**
   - Payment Entry is submitted and posted to Accounts
   - GL Entries created
   - Customer notification triggered
   - Final state (can only be cancelled)

9. **Cancelled**
   - Payment has been cancelled
   - GL Entries reversed
   - Outstanding amount restored on invoice

### Workflow Transitions

```
Draft → Pending Deduction Approval (Submit with Deductions by Salesperson)
Draft → Pending Payment Approval (Submit without Deductions by Salesperson)

Pending Deduction Approval → Deduction Approved (Approve Deductions by Manager)
Pending Deduction Approval → Deduction Rejected (Reject Deductions by Manager)
Deduction Rejected → Draft (Revise by Salesperson)

Deduction Approved → Pending Payment Approval (Auto-transition)

Pending Payment Approval → Approved (Approve Payment by Manager)
Pending Payment Approval → Rejected (Reject Payment by Manager)
Rejected → Draft (Revise by Salesperson)

Approved → Submitted (Submit to Accounts by Salesperson/Manager)

Submitted → Cancelled (Cancel by Manager)
```

### Creating the Workflow

1. **Navigate to Workflow**
   - Go to **Setup** → **Workflow** → **Workflow**
   - Click **New**

2. **Configure Workflow**
   - **Document Type**: Payment Entry
   - **Workflow Name**: Payment Entry Approval Workflow
   - **Is Active**: Yes
   - **Override Status**: Yes (to use custom workflow states)

3. **Add Workflow States**

| State | Doc Status | Allow Edit | Style |
|-------|-----------|-----------|-------|
| Draft | 0 (Draft) | Salesperson, Manager | Primary |
| Pending Deduction Approval | 0 (Draft) | Manager | Warning |
| Deduction Approved | 0 (Draft) | Manager | Info |
| Deduction Rejected | 0 (Draft) | Salesperson, Manager | Danger |
| Pending Payment Approval | 0 (Draft) | Manager | Warning |
| Approved | 0 (Draft) | Salesperson, Manager | Success |
| Rejected | 0 (Draft) | Salesperson, Manager | Danger |
| Submitted | 1 (Submitted) | - | Success |
| Cancelled | 2 (Cancelled) | - | Danger |

4. **Add Workflow Transitions**

| From State | To State | Action | Allowed Role | Condition |
|-----------|---------|--------|--------------|-----------|
| Draft | Pending Deduction Approval | Submit with Deductions | Salesperson | has_deductions = 1 |
| Draft | Pending Payment Approval | Submit for Approval | Salesperson | has_deductions = 0 |
| Pending Deduction Approval | Deduction Approved | Approve Deductions | Manager | - |
| Pending Deduction Approval | Deduction Rejected | Reject Deductions | Manager | - |
| Deduction Rejected | Draft | Revise | Salesperson | - |
| Deduction Approved | Pending Payment Approval | Submit for Payment Approval | Salesperson | - |
| Pending Payment Approval | Approved | Approve Payment | Manager | - |
| Pending Payment Approval | Rejected | Reject Payment | Manager | - |
| Rejected | Draft | Revise | Salesperson | - |
| Approved | Submitted | Submit to Accounts | Salesperson, Manager | - |
| Submitted | Cancelled | Cancel | Manager | - |

5. **Save Workflow**
   - Click **Save**
   - The workflow is now active for all Payment Entries

### Workflow Permissions

Configure role-based permissions:

#### Salesperson Permissions
- Create new Payment Entry
- Edit Draft Payment Entry
- Submit for Approval (with or without discount)
- View all states
- Cannot approve discount or payment
- Can submit to Accounts after Manager approval

#### Manager Permissions
- All Salesperson permissions
- Approve/Reject Discount
- Approve/Reject Payment
- Cancel Payment Entry
- Override all restrictions

---

## Creating Payment Entry from Sales Invoice

### User Journey - Salesperson

#### Scenario 1: Payment Without Discount

1. **Navigate to Sales Invoice**
   - Open the submitted Sales Invoice
   - Check the outstanding amount

2. **Click "Create Payment Entry" Button**
   - ERPNext provides a default "Create" → "Payment" button
   - This creates a new Payment Entry linked to the invoice

3. **Payment Entry Auto-Population**
   - System creates a new Payment Entry with:
     - `payment_type` = "Receive"
     - `party_type` = "Customer"
     - `party` = Customer from invoice
     - `paid_amount` = Outstanding amount
     - References table populated with invoice details
     - `total_allocated_amount` = Invoice outstanding amount

4. **Enter Payment Details**
   - Select `mode_of_payment` (Cash, Bank, UPI, etc.)
   - Verify `posting_date` (current date by default)
   - If paying partial amount, adjust `paid_amount`
   - Ensure `difference_amount` = 0 (fully allocated)
   - Add any remarks in the `remarks` field

5. **Ensure No Deductions Applied**
   - Keep the "Deductions or Loss" table empty
   - Do not add any deduction rows

6. **Save as Draft**
   - Click **Save** to save as Draft
   - Review all details

7. **Submit for Payment Approval**
   - Click **Submit for Approval** button
   - Workflow transitions to "Pending Payment Approval"
   - Manager receives notification (optional)

8. **Wait for Manager Approval**
   - Payment Entry status shows "Pending Payment Approval"
   - Salesperson cannot edit at this stage

9. **After Manager Approval**
   - Workflow transitions to "Approved"
   - `payment_approval_status` = "Approved"
   - `approved_by` = Manager name
   - `approval_date` = Current timestamp

10. **Submit to Accounts**
    - Click **Submit to Accounts** button
    - Payment Entry is submitted (docstatus = 1)
    - GL Entries are created automatically
    - Sales Invoice outstanding amount is updated
    - Customer notification is triggered
    - Workflow transitions to "Submitted"

#### Scenario 2: Payment With Discount

1. **Navigate to Sales Invoice**
   - Open the submitted Sales Invoice
   - Check the outstanding amount

2. **Create Payment Entry**
   - Click "Create" → "Payment"
   - Payment Entry is created with invoice details

3. **Enter Payment Details**
   - Select `mode_of_payment`
   - Verify `posting_date`
   - Enter `paid_amount` (may be less than outstanding if discount applied)

4. **Apply Discount Using Deductions Table**
   - Scroll to the **"Deductions or Loss"** section
   - Click **Add Row** in the deductions table
   - Select `account` = "Discount Allowed" (or your discount expense account)
   - Select `cost_center` = "Main" (or appropriate cost center)
   - Enter `amount` = Discount amount (e.g., ₹500)
   - System automatically adjusts `paid_amount` = Outstanding - Deduction
   - Enter `deduction_reason` field (mandatory)
     - Example: "Bulk order discount", "Repeat customer discount", "Promotional offer"
   - Check `has_deductions` = 1 (auto-set by system)

5. **Save as Draft**
   - Click **Save**
   - Review deduction calculations
   - Verify: `paid_amount` + `total_deductions` = Invoice outstanding

6. **Submit for Deduction Approval**
   - Click **Submit with Deductions** button
   - Workflow transitions to "Pending Deduction Approval"
   - `deduction_approval_status` = "Pending"
   - Manager receives notification for deduction approval

7. **Wait for Deduction Approval**
   - Payment Entry status shows "Pending Deduction Approval"
   - Salesperson cannot edit at this stage

8. **After Deduction Approval by Manager**
   - Workflow transitions to "Deduction Approved"
   - `deduction_approval_status` = "Approved"
   - `deduction_approved_by` = Manager name
   - `deduction_approval_date` = Current timestamp

9. **Submit for Payment Approval**
   - Click **Submit for Payment Approval** button
   - Workflow transitions to "Pending Payment Approval"
   - Manager receives notification for payment approval

10. **Wait for Payment Approval**
    - Payment Entry status shows "Pending Payment Approval"
    - Salesperson cannot edit at this stage

11. **After Payment Approval by Manager**
    - Workflow transitions to "Approved"
    - `payment_approval_status` = "Approved"
    - `approved_by` = Manager name
    - `approval_date` = Current timestamp

12. **Submit to Accounts**
    - Click **Submit to Accounts** button
    - Payment Entry is submitted (docstatus = 1)
    - GL Entries are created automatically:
      - Bank/Cash account debited with paid amount
      - Discount Allowed account debited with deduction amount
      - Debtors account credited with total (paid + deduction)
    - Sales Invoice outstanding amount is updated
    - Customer notification is triggered
    - Workflow transitions to "Submitted"

### User Journey - Manager

#### Approving Deductions (if applicable)

1. **Receive Notification**
   - Manager receives notification that a Payment Entry with deductions is pending approval
   - Notification includes deduction account, amount, and reason

2. **Open Payment Entry**
   - Navigate to Payment Entry
   - Status shows "Pending Deduction Approval"

3. **Review Deduction Details**
   - Scroll to "Deductions or Loss" section
   - Check deduction table entries:
     - Account (should be "Discount Allowed")
     - Cost Center
     - Amount
   - Review `deduction_reason`
   - Verify if deduction is justified
   - Check customer history and payment patterns
   - Ensure deduction account is correct

4. **Approve or Reject Deductions**
   - **If Approved**:
     - Click **Approve Deductions** button
     - Workflow transitions to "Deduction Approved"
     - `deduction_approval_status` = "Approved"
     - `deduction_approved_by` = Current Manager
     - `deduction_approval_date` = Current timestamp
     - Salesperson can now submit for payment approval
   
   - **If Rejected**:
     - Click **Reject Deductions** button
     - Enter `rejection_reason` in the dialog
     - Example: "Deduction amount too high", "No justification provided", "Wrong account selected"
     - Workflow transitions to "Deduction Rejected"
     - Salesperson can revise deductions or remove them

#### Approving Payment

1. **Receive Notification**
   - Manager receives notification that a Payment Entry is pending payment approval

2. **Open Payment Entry**
   - Navigate to Payment Entry
   - Status shows "Pending Payment Approval"

3. **Review Payment Details**
   - Verify customer details
   - Check payment amount and mode
   - Review invoice references
   - Ensure allocation is correct
   - If deductions were applied, verify they were previously approved

4. **Approve or Reject Payment**
   - **If Approved**:
     - Click **Approve Payment** button
     - Workflow transitions to "Approved"
     - `payment_approval_status` = "Approved"
     - `approved_by` = Current Manager
     - `approval_date` = Current timestamp
     - Salesperson can now submit to Accounts
   
   - **If Rejected**:
     - Click **Reject Payment** button
     - Enter `rejection_reason` in the dialog
     - Example: "Incorrect payment mode", "Amount mismatch", "Missing documentation"
     - Workflow transitions to "Rejected"
     - Salesperson can revise and resubmit

---

## Customer Notification on Payment Submission

### Notification Trigger

When a Payment Entry is **submitted to Accounts**, the system must automatically send a notification to the customer via **Email and WhatsApp**.

### Implementation Approach

We will use **Frappe's Document Events Hook** to trigger the notification when the Payment Entry is submitted.

### Function Declaration

#### File Location
```
fabric_sense/fabric_sense/py/payment_entry.py

#### Function Name
```python
send_customer_payment_notification
```

#### Function Purpose
This function will:
1. Detect when a Payment Entry is submitted (docstatus = 1)
2. Retrieve customer contact details (email, phone number)
3. Prepare notification content with payment details
4. Send Email notification using Frappe's email API
5. Send WhatsApp notification using WhatsApp Business API
6. Update the Payment Entry to mark notification as sent
7. Log notification status for tracking

#### Function Signature
```python
def send_customer_payment_notification(doc, method=None):
    """
    Send email and WhatsApp notification to customer when Payment Entry is submitted.
    
    Args:
        doc (Document): Payment Entry document object
        method (str): Event method name (e.g., 'on_submit')
    
    Returns:
        None
    
    Raises:
        Exception: If notification sending fails
    """
```

### Registering the Hook

To trigger the notification function when a Payment Entry is submitted, we need to register it in the `hooks.py` file.

#### File Location
```
fabric_sense/fabric_sense/hooks.py
```

#### Hook Configuration

Add the following to the `doc_events` section in `hooks.py`:

```python
doc_events = {
    "Payment Entry": {
        "on_submit": "fabric_sense.fabric_sense.py.payment_entry.send_customer_payment_notification",
    }
}
```

**Explanation:**
- **`on_submit`**: Triggers when the Payment Entry is submitted
- The function checks if `payment_type == "Receive"` and `party_type == "Customer"` before sending
- Notification is sent only once (tracked by `customer_notification_sent` field)

---

## Notification Content Templates

### Email Template

**Subject:** Payment Received - Receipt #{payment_entry_number} - Fabric Sense

**Body:**
```
Dear {customer_name},

Thank you for your payment! We have successfully received your payment for the following invoice(s).

Payment Receipt Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Receipt Number: {payment_entry_number}
Payment Date: {posting_date}
Payment Mode: {mode_of_payment}
Amount Paid: ₹{paid_amount}
{discount_info}

Invoice Details:
{invoice_list}

Total Amount Received: ₹{received_amount}
Outstanding Balance: ₹{outstanding_amount}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{payment_status_message}

You can download your payment receipt at:
{receipt_url}

If you have any questions regarding this payment, please contact us at:
📞 {company_phone}
📧 {company_email}

Thank you for your business!

Best regards,
Fabric Sense Team
```

**Deduction Info Template (if applicable):**
```
Discount Applied: ₹{deduction_amount}
Reason: {deduction_reason}
```

**Payment Status Messages:**
- If fully paid: "Your invoice has been fully paid. Thank you!"
- If partial payment: "Remaining balance: ₹{remaining_balance}. Please clear the balance at your earliest convenience."

### WhatsApp Template

```
✅ *Payment Received!*

Dear {customer_name},

Thank you for your payment! 🙏

💰 *Payment Details:*
• Receipt No: {payment_entry_number}
• Date: {posting_date}
• Mode: {mode_of_payment}
• Amount: ₹{paid_amount}
{discount_info_whatsapp}

📄 *Invoice:* {invoice_numbers}
💵 *Outstanding:* ₹{outstanding_amount}

{payment_status_emoji} {payment_status_message}

Download receipt: {short_url}

Thank you for choosing Fabric Sense! ✨
```

**Deduction Info WhatsApp (if applicable):**
```
• Discount: ₹{deduction_amount}
```

---

## Deduction Handling and Validation

### Automatic Calculation

ERPNext's Payment Entry automatically handles deduction calculations:

1. **When deduction is added to the table**:
   - System calculates `total_deductions` = Sum of all deduction amounts
   - System adjusts `paid_amount` = `total_allocated_amount` - `total_deductions`
   - This happens automatically in ERPNext's standard code

2. **Payment Amount Validation**:
   - The system validates: `paid_amount` + `total_deductions` = `total_allocated_amount`
   - If equation doesn't balance, error is shown

### Implementation in Client Script

**File:** `fabric_sense/fabric_sense/custom/payment_entry.js`

```javascript
frappe.ui.form.on('Payment Entry', {
    refresh: function(frm) {
        // Auto-set has_deductions flag when deductions table has entries
        if (frm.doc.deductions && frm.doc.deductions.length > 0) {
            frm.set_value('has_deductions', 1);
        } else {
            frm.set_value('has_deductions', 0);
        }
    },
    
    validate: function(frm) {
        // Validate deduction reason is provided when deductions exist
        if (frm.doc.has_deductions && !frm.doc.deduction_reason) {
            frappe.msgprint(__('Please provide a reason for the deduction'));
            frappe.validated = false;
        }
        
        // Validate deduction accounts
        if (frm.doc.deductions) {
            frm.doc.deductions.forEach(function(row) {
                if (!row.account) {
                    frappe.msgprint(__('Please select an account for all deduction rows'));
                    frappe.validated = false;
                }
            });
        }
    }
});

// Child table event for deductions
frappe.ui.form.on('Payment Entry Deduction', {
    deductions_add: function(frm, cdt, cdn) {
        // Set default account to "Discount Allowed" when new row is added
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'account', 'Discount Allowed');
        frm.set_value('has_deductions', 1);
    },
    
    deductions_remove: function(frm) {
        // Update has_deductions flag when row is removed
        if (!frm.doc.deductions || frm.doc.deductions.length === 0) {
            frm.set_value('has_deductions', 0);
        }
    },
    
    amount: function(frm, cdt, cdn) {
        // ERPNext automatically recalculates paid_amount
        // No manual intervention needed
        frm.refresh_field('paid_amount');
    }
});
```

---

## GL Entry Creation with Deductions

### Standard Payment Entry GL Entries

When a Payment Entry is submitted without deductions:

| Account | Debit | Credit |
|---------|-------|--------|
| Bank/Cash Account | Paid Amount | - |
| Debtors (Accounts Receivable) | - | Paid Amount |

### Payment Entry with Deductions GL Entries

When a Payment Entry is submitted with deductions (discount):

| Account | Debit | Credit |
|---------|-------|--------|
| Bank/Cash Account | Paid Amount | - |
| Discount Allowed Account | Deduction Amount | - |
| Debtors (Accounts Receivable) | - | Paid Amount + Deduction Amount |

**Example:**
- Invoice Outstanding: ₹10,000
- Discount (Deduction): ₹500
- Paid Amount: ₹9,500

**GL Entries:**
| Account | Debit | Credit |
|---------|-------|--------|
| Bank/Cash | ₹9,500 | - |
| Discount Allowed | ₹500 | - |
| Debtors | - | ₹10,000 |

### How ERPNext Handles This Automatically

ERPNext's Payment Entry automatically creates GL entries for deductions:

1. **For each row in the Deductions table**:
   - Creates a GL Entry debiting the specified account (e.g., "Discount Allowed")
   - Amount = deduction amount
   - Cost Center = specified cost center

2. **For the payment**:
   - Debits Bank/Cash account with `paid_amount`
   - Credits Debtors account with `total_allocated_amount`

3. **No custom code needed** - ERPNext handles this in its standard Payment Entry submission logic

### Discount Account Setup

Ensure the "Discount Allowed" account exists in your Chart of Accounts:

1. **Navigate to Chart of Accounts**
   - Go to **Accounting** → **Chart of Accounts**

2. **Check if "Discount Allowed" exists**
   - Look under "Expenses" → "Indirect Expenses"
   - If not found, create it:
     - Account Name: "Discount Allowed"
     - Account Type: "Expense Account"
     - Parent Account: "Indirect Expenses"

---

## Handling Multiple Invoices

### Scenario: Payment Against Multiple Invoices

A customer may want to pay for multiple invoices in a single payment.

#### Process:

1. **Create Payment Entry**
   - Click "Create" → "Payment Entry" from any invoice
   - Or create a new Payment Entry directly

2. **Add Multiple Invoice References**
   - In the "References" table, add multiple rows
   - Each row links to a different Sales Invoice
   - Specify the allocated amount for each invoice

3. **Apply Deduction (if applicable)**
   - Add row in "Deductions or Loss" table
   - Select "Discount Allowed" account
   - Enter deduction amount
   - The deduction applies to the total payment, not individual invoices
   - Specify the reason in `deduction_reason`

4. **Validation**
   - Ensure: `paid_amount + total_deductions = sum(allocated_amounts)`
   - Each invoice's allocated amount should not exceed its outstanding

5. **Approval Process**
   - Same workflow applies (deduction approval → payment approval)
   - Manager reviews all invoice references and deductions

---

## Partial Payments

### Scenario: Customer Pays Partial Amount

A customer may pay only a portion of the invoice amount.

#### Process:

1. **Create Payment Entry**
   - Payment Entry is created from Sales Invoice

2. **Enter Partial Amount**
   - Enter `paid_amount` less than invoice outstanding
   - Do not apply discount (unless partial payment includes discount)

3. **Allocation**
   - System allocates the paid amount to the invoice
   - Invoice outstanding is reduced by paid amount
   - Invoice status remains "Partly Paid"

4. **Approval**
   - Manager approves the partial payment
   - No special approval needed for partial payments (unless deductions applied)

5. **Submit to Accounts**
   - Payment is posted
   - Invoice outstanding is updated
   - Customer can make additional payments later

#### Subsequent Payments

- Create new Payment Entry for the remaining amount
- System shows updated outstanding amount
- Process repeats until invoice is fully paid

---

## Payment Entry Validation Rules

### Server-Side Validations

Implement the following validations in `payment_entry.py`:

1. **Deduction Validation**
   ```python
   if doc.has_deductions:
       if not doc.deduction_reason:
           frappe.throw("Deduction reason is mandatory when deductions are applied")
       
       # Validate deduction table entries
       if not doc.deductions or len(doc.deductions) == 0:
           frappe.throw("Deductions table cannot be empty when has_deductions is checked")
       
       # Validate each deduction row has an account
       for deduction in doc.deductions:
           if not deduction.account:
               frappe.throw("Please select an account for all deduction rows")
       
       # Validate total deductions
       total_deductions = sum([d.amount for d in doc.deductions])
       if total_deductions > doc.total_allocated_amount:
           frappe.throw("Total deductions cannot exceed total allocated amount")
   ```

2. **Approval Validation**
   ```python
   if doc.has_deductions and doc.workflow_state == "Pending Payment Approval":
       if doc.deduction_approval_status != "Approved":
           frappe.throw("Deductions must be approved before payment approval")
   ```

3. **Submission Validation**
   ```python
   if doc.docstatus == 1:  # Submitted
       if doc.payment_approval_status != "Approved":
           frappe.throw("Payment must be approved by Manager before submission")
       
       # Additional validation for deductions
       if doc.has_deductions and doc.deduction_approval_status != "Approved":
           frappe.throw("Deductions must be approved before submission")
   ```

4. **Amount Validation**
   ```python
   # ERPNext handles this automatically, but we can add extra validation
   total_deductions = sum([d.amount for d in doc.deductions]) if doc.deductions else 0
   total_expected = doc.paid_amount + total_deductions
   
   if abs(total_expected - doc.total_allocated_amount) > 0.01:  # Allow small rounding difference
       frappe.throw(f"Payment amount ({doc.paid_amount}) plus deductions ({total_deductions}) must equal allocated amount ({doc.total_allocated_amount})")
   ```

---

## Reference Documents

- [Sales Invoice Creation Guide](./sales_invoice_creation.md)
- [Sales Order Creation Guide](./sales_order_creation.md)
- [Delivery Note Creation Guide](./delivery_note_creation.md)
- [Case I Implementation](../case-i-implementation.md)
- [Case II Implementation](../case-ii-implementation.md)
- [Overview](../overview.md)

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Author**: Fabric Sense Development Team
