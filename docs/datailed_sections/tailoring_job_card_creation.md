# Tailoring Job Card Creation Guidelines

## Overview

The Tailoring Job Card is a critical document in the Fabric Sense application that manages the tailoring process from assignment to completion. It tracks tailor assignments, work progress, material consumption, costs, and payment status. The Job Card is created after the Tailoring Sheet is finalized and all required materials are ready for the tailoring work.

## Doctype: Tailoring Job Card

### Purpose
- Assign tailoring work to a specific tailor
- Track tailoring job start and end dates
- Manage tailoring charges and travelling charges
- Automatically update job status based on dates
- Track material consumption when tailoring starts
- Calculate total tailoring costs
- Monitor tailor payment status
- Integrate with stock management for material consumption
- Link to Sales Invoice for final billing

---

## Field Structure

### Basic Information Fields

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `naming_series` | Data | Auto-naming series (e.g., TJC-.YYYY.-.####) | Yes |
| `tailoring_sheet` | Link (Tailoring Sheet) | Reference to tailoring sheet | Yes |
| `customer` | Link (Customer) | Reference to the customer | Yes |
| `project` | Link (Project) | Reference to the project | Yes |
| `sales_order` | Link (Sales Order) | Reference to the sales order | No |
| `job_card_date` | Date | Date when job card was created | Yes |
| `status` | Select | Draft, Assigned, Started, Completed, Invoiced | Yes |

### Tailor Assignment Fields

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `assigned_tailor` | Link (Tailors) | Tailor assigned for the job | Yes |
| `tailor_name` | Data | Tailor's full name | Auto-filled |
| `tailor_contact` | Data | Tailor's contact number | Auto-filled |
| `tailor_email` | Data | Tailor's email address | Auto-filled |

### Job Schedule Fields

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `expected_start_date` | Date | Expected job start date | Yes |
| `expected_end_date` | Date | Expected job completion date | Yes |
| `actual_start_date` | Date | Actual date when job started | Auto-set |
| `actual_end_date` | Date | Actual date when job completed | Auto-set |
| `expected_duration_days` | Int | Expected duration in days | Auto-calculated |
| `actual_duration_days` | Int | Actual duration in days | Auto-calculated |
| `delay_days` | Int | Delay in days (if any) | Auto-calculated |

### Cost Fields

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `tailoring_charge` | Currency | Base charge for tailoring work | Yes |
| `travelling_charge` | Currency | Additional charge for site visit/delivery | No |
| `total_tailoring_cost` | Currency | Total cost (tailoring + travelling) | Auto-calculated |
| `cost_per_day` | Currency | Cost per day of work | Auto-calculated |

### Material Details (Child Table)

**Child Table Name:** `material_details`

This table lists all materials required for the tailoring job.

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `item` | Link (Item) | Item to be consumed | Yes |
| `item_name` | Data | Item name | Auto-filled |
| `description` | Text | Item description | Auto-filled |
| `quantity` | Float | Quantity required | Yes |
| `uom` | Link (UOM) | Unit of measurement | Yes |
| `warehouse` | Link (Warehouse) | Source warehouse | Yes |
| `stock_available` | Float | Current stock availability | Auto-fetched |
| `rate` | Currency | Rate per unit | Yes |
| `amount` | Currency | Total amount | Auto-calculated |
| `consumed` | Check | Whether material consumed | Auto-updated |
| `consumption_date` | Datetime | When material was consumed | Auto-updated |

### Job Status Tracking

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `job_status` | Select | Not Started, Started, In Progress, Completed | Auto-updated |
| `completion_percentage` | Percent | Job completion percentage | No |
| `material_issued` | Check | Whether materials issued to tailor | Auto-updated |
| `material_issue_date` | Datetime | When materials were issued | Auto-updated |
| `stock_entry_reference` | Link (Stock Entry) | Reference to stock entry | Auto-updated |

### Quality Check Fields

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `quality_check_required` | Check | Whether quality check is required | No |
| `quality_check_status` | Select | Pending, Passed, Failed, Not Required | Auto-updated |
| `quality_checked_by` | Link (User) | User who performed quality check | No |
| `quality_check_date` | Datetime | Quality check timestamp | No |
| `quality_remarks` | Text | Quality check remarks | No |
| `rework_required` | Check | Whether rework is needed | No |
| `rework_reason` | Text | Reason for rework | No |

### Payment Tracking Fields

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `tailor_payment_status` | Select | Unpaid, Partially Paid, Paid | Auto-updated |
| `tailor_payment_type` | Select | Per Job, Monthly | Yes |
| `tailor_payment_amount` | Currency | Amount paid to tailor | No |
| `tailor_payment_date` | Date | Payment date | No |
| `tailor_payment_reference` | Link (Payment Entry) | Reference to payment entry | No |
| `payment_due_date` | Date | When payment is due to tailor | Auto-calculated |

### Notification Tracking

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `assignment_notification_sent` | Check | Assignment notification sent | Auto-updated |
| `assignment_notification_date` | Datetime | When assignment notification sent | Auto-updated |
| `start_notification_sent` | Check | Start notification sent | Auto-updated |
| `start_notification_date` | Datetime | When start notification sent | Auto-updated |
| `completion_notification_sent` | Check | Completion notification sent | Auto-updated |
| `completion_notification_date` | Datetime | When completion notification sent | Auto-updated |

### Additional Information

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `special_instructions` | Text Editor | Special instructions for tailor | No |
| `customer_requirements` | Text Editor | Specific customer requirements | No |
| `memo` | Text Editor | Internal notes and remarks | No |

### Audit Fields

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `created_by` | Link (User) | User who created the record | Auto |
| `created_date` | Datetime | Creation timestamp | Auto |
| `modified_by` | Link (User) | Last modified by | Auto |
| `modified_date` | Datetime | Last modification timestamp | Auto |

---

## Status Workflow

### Status Options

1. **Draft** - Initial state when job card is created
2. **Assigned** - When job card is submitted and tailor is notified
3. **Started** - When tailoring work has begun (auto-updated when actual_start_date is set)
4. **Completed** - When tailoring work is finished (auto-updated when actual_end_date is set)
5. **Invoiced** - When Sales Invoice is created for the completed work

### Job Status Options

1. **Not Started** - Materials not yet issued, work not begun
2. **Started** - Tailoring work has begun (auto-updated when actual_start_date is set)
3. **In Progress** - Tailoring work ongoing
4. **Completed** - Tailoring work finished (auto-updated when actual_end_date is set)

### Status Transitions

```
Draft → Assigned (Submit by Salesperson, triggers tailor notification)
Assigned → Started (Auto-update when actual_start_date is set to current date)
Started → Completed (Auto-update when actual_end_date is set)
Completed → Invoiced (When Sales Invoice is created)
```

### Automatic Status Updates

The system automatically updates the job status based on dates:

1. **When current date = expected_start_date**:
   - If status = "Assigned", auto-update to "Started"
   - Set `actual_start_date` = current date
   - Update `job_status` = "Started"
   - Create Stock Entry to consume materials
   - Send start notification to salesperson and manager

2. **When actual_end_date is set**:
   - Auto-update status to "Completed"
   - Update `job_status` = "Completed"
   - Calculate `actual_duration_days`
   - Calculate `delay_days` (if any)
   - Send completion notification to salesperson, manager, and customer

### Permissions Based on Status

- **Draft**: Can be edited and deleted
- **Assigned**: Limited editing, can update dates and charges
- **Started**: Read-only except for completion date and quality check
- **Completed**: Read-only, can create Sales Invoice
- **Invoiced**: Read-only, can only be cancelled by Manager

---

## Creation Process

### Prerequisites

Before creating a Tailoring Job Card:

1. **Tailoring Sheet must be finalized**
   - Status = "Submitted" or "Approved"
   - All adjustments completed
   - Final material requirements calculated

2. **Materials must be available**
   - All items in `final_material_requirements` must be in stock
   - Material Requests fulfilled
   - Stock updated from Purchase Receipts (if applicable)

3. **Tailor must be selected**
   - Valid Tailor record exists
   - Tailor is available for the expected dates
   - Tailor has required skills for the job

### Automatic Creation from Tailoring Sheet

When all materials are ready, create a Tailoring Job Card:

1. **Trigger**: "Create Tailoring Job Card" button on Tailoring Sheet
2. **Process**:
   - Copy tailoring sheet reference
   - Copy customer and project details
   - Copy assigned tailor information
   - Copy expected start and end dates
   - Copy tailoring charge and travelling charge
   - Populate material_details table from tailoring sheet's final_material_requirements
   - Set status to "Draft"
3. **Outcome**: New Tailoring Job Card created with all details

### Manual Entry

Salesperson can also create a Tailoring Job Card manually:

1. Navigate to Tailoring Job Card list
2. Click "New"
3. Select Tailoring Sheet (auto-populates customer, project, materials)
4. Select Assigned Tailor
5. Enter expected start and end dates
6. Enter tailoring charge and travelling charge
7. Review material details
8. Add special instructions (if any)
9. Save as Draft
10. Submit to assign the job

---

## Calculation Formulas

### Expected Duration
```
Expected Duration Days = Expected End Date - Expected Start Date
```

### Actual Duration
```
Actual Duration Days = Actual End Date - Actual Start Date
```

### Delay Calculation
```
Delay Days = Actual End Date - Expected End Date
If Delay Days < 0, then Delay Days = 0
```

### Total Tailoring Cost
```
Total Tailoring Cost = Tailoring Charge + Travelling Charge
```

### Cost Per Day
```
Cost Per Day = Total Tailoring Cost / Actual Duration Days
(Calculated after job completion)
```

### Material Amount
```
Material Amount = Quantity × Rate
```

### Total Material Cost
```
Total Material Cost = Sum of all Material Amounts
```

---

## Validation Rules

### Mandatory Field Validations

1. Tailoring Sheet reference is mandatory
2. Customer and Project must be selected
3. Assigned Tailor is mandatory
4. Expected Start Date and End Date are mandatory
5. Tailoring Charge must be specified
6. At least one material detail must exist

### Business Logic Validations

1. **Date Validations**:
   - Expected End Date must be after Expected Start Date
   - Actual End Date must be after Actual Start Date
   - Actual Start Date cannot be in the future
   - Expected Start Date should not be in the past (warning only)

2. **Material Validations**:
   - All materials must have sufficient stock available
   - Material quantities must be greater than 0
   - Warehouse must be specified for each material
   - Material rates must be greater than 0

3. **Status Transition Validations**:
   - Cannot move to "Started" without material availability
   - Cannot mark "Completed" without actual end date
   - Cannot create Sales Invoice unless status = "Completed"
   - Cannot modify job card after status = "Invoiced"

4. **Tailor Validations**:
   - Tailor must be active
   - Tailor should not have overlapping job assignments (warning only)
   - Tailor contact details must be available for notifications

5. **Cost Validations**:
   - Tailoring charge must be greater than 0
   - Travelling charge must be 0 or greater
   - Total cost must not exceed predefined limits (configurable)

---

## Automatic Stock Update on Job Start

### Stock Entry Creation

When the tailoring job starts (status changes to "Started"), the system must automatically create a Stock Entry to consume materials.

### Stock Entry Details

**Purpose**: Material Consumption  
**Stock Entry Type**: Material Issue  
**From Warehouse**: Warehouse specified in material_details  
**To Warehouse**: Work In Progress (WIP) or Tailoring Warehouse  

### Stock Entry Items

For each row in `material_details` table:
- Item Code: From material_details.item
- Quantity: From material_details.quantity
- Rate: From material_details.rate
- Amount: Auto-calculated
- Source Warehouse: From material_details.warehouse
- Target Warehouse: WIP/Tailoring Warehouse

### Process Flow

1. **Trigger**: When actual_start_date is set to current date
2. **Validation**:
   - Check stock availability for all materials
   - Ensure all materials have valid warehouse
   - Verify material quantities match tailoring sheet
3. **Stock Entry Creation**:
   - Create new Stock Entry document
   - Set purpose = "Material Issue"
   - Populate items from material_details table
   - Set posting date = actual_start_date
   - Set reference to Tailoring Job Card
4. **Stock Entry Submission**:
   - Auto-submit the Stock Entry
   - Update stock balances
   - Create GL Entries for inventory valuation
5. **Job Card Update**:
   - Set `material_issued` = 1
   - Set `material_issue_date` = current datetime
   - Set `stock_entry_reference` = Stock Entry name
   - Update each material row: `consumed` = 1, `consumption_date` = current datetime
6. **Notification**:
   - Send notification to salesperson and manager
   - Notify that materials have been consumed

### Implementation

**Function Location**: `fabric_sense/fabric_sense/py/tailoring_job_card.py`

**Function Name**: `create_material_consumption_entry`

**Function Signature**:
```python
def create_material_consumption_entry(doc, method=None):
    """
    Create Stock Entry for material consumption when tailoring job starts.
    
    Args:
        doc (Document): Tailoring Job Card document object
        method (str): Event method name
    
    Returns:
        str: Stock Entry name
    
    Raises:
        Exception: If stock entry creation fails
    """
```

**Hook Registration** in `hooks.py`:
```python
doc_events = {
    "Tailoring Job Card": {
        "on_update": "fabric_sense.fabric_sense.py.tailoring_job_card.auto_update_job_status",
    }
}
```

---

## Tailoring Cost Calculation

### Cost Components

The total tailoring cost includes:

1. **Base Tailoring Charge**:
   - Charge for the actual stitching/tailoring work
   - Can be per job or per item
   - Specified in the Tailoring Job Card

2. **Travelling Charge**:
   - Additional charge for site visit (measurement or delivery)
   - Applied when tailor visits customer location
   - Optional field

### Calculation Method

```
Total Tailoring Cost = Tailoring Charge + Travelling Charge
```

### Cost Tracking

The system tracks:
- **Expected Cost**: Entered at job card creation
- **Actual Cost**: Calculated after job completion
- **Cost Per Day**: Total cost divided by actual duration
- **Material Cost**: Separate from tailoring cost
- **Total Project Cost**: Material cost + Tailoring cost

### Integration with Sales Invoice

When creating Sales Invoice:
- Add line item for "Tailoring Services"
- Amount = Total Tailoring Cost
- Add line item for "Travelling Charges" (if applicable)
- Amount = Travelling Charge
- Material costs added separately from Sales Order

---

## Tailor Payment Tracking

### Payment Types

1. **Per Job Payment**:
   - Tailor is paid for each completed job
   - Payment created immediately after job completion
   - Amount = Total Tailoring Cost for that job

2. **Monthly Payment**:
   - Tailor is paid monthly for all completed jobs
   - Payment created at end of month
   - Amount = Sum of all completed jobs in that month

### Payment Status Options

1. **Unpaid** - No payment made yet
2. **Partially Paid** - Partial payment made (for monthly payment type)
3. **Paid** - Full payment completed

### Payment Process

#### For Per Job Payment:

1. **After Job Completion**:
   - Status changes to "Completed"
   - `tailor_payment_status` = "Unpaid"
   - `payment_due_date` = Completion date + 7 days (configurable)

2. **Create Payment Entry**:
   - Salesperson creates Payment Entry
   - Party Type = "Supplier" or "Tailor" (custom party type)
   - Party = Assigned Tailor
   - Amount = Total Tailoring Cost
   - Reference = Tailoring Job Card

3. **Manager Approval**:
   - Manager reviews and approves payment
   - Similar to customer payment approval workflow

4. **Payment Submission**:
   - Payment Entry submitted
   - GL Entries created
   - Job Card updated:
     - `tailor_payment_status` = "Paid"
     - `tailor_payment_amount` = Total Tailoring Cost
     - `tailor_payment_date` = Payment date
     - `tailor_payment_reference` = Payment Entry name

#### For Monthly Payment:

1. **End of Month**:
   - System generates report of all completed jobs for each tailor
   - Calculates total amount due

2. **Create Consolidated Payment Entry**:
   - One Payment Entry per tailor
   - Amount = Sum of all completed jobs
   - References = All Tailoring Job Cards for that month

3. **Approval and Submission**:
   - Same approval workflow as per job payment
   - All referenced job cards updated with payment details

### Payment Tracking Fields

The following fields track payment status:
- `tailor_payment_status`: Current payment status
- `tailor_payment_type`: Per Job or Monthly
- `tailor_payment_amount`: Amount paid
- `tailor_payment_date`: When payment was made
- `tailor_payment_reference`: Link to Payment Entry
- `payment_due_date`: When payment is due

---

## Integration Points

### 1. Tailoring Sheet Integration

- Job Card created from Tailoring Sheet
- All material requirements copied from tailoring sheet
- Tailor assignment and dates copied
- Link maintained for traceability
- Changes in Tailoring Sheet do not affect Job Card after creation

### 2. Project Integration

- Job Card linked to Project
- Job Card task created in Project task list
- Task status updates based on job_status
- Project progress tracked
- Project timeline updated based on actual dates

### 3. Stock Entry Integration

- Stock Entry created automatically when job starts
- Materials consumed immediately
- Stock updated for all items in material_details
- Warehouse transactions recorded
- Inventory valuation updated

### 4. Sales Invoice Integration

- Sales Invoice created when status = "Completed"
- Invoice includes:
  - Material cost (from Sales Order)
  - Tailoring charge
  - Travelling charge
- Customer notified via WhatsApp/Email
- Job Card status updated to "Invoiced"

### 5. Tailor Integration

- Assigned Tailor receives notification on assignment
- Tailor can view job card details
- Payment tracking for tailor work
- Performance metrics tracked (completion time, quality)
- Tailor workload management

### 6. Sales Order Integration

- Job Card linked to Sales Order
- Sales Order items include tailoring services
- Pricing updates reflect tailoring costs
- Delivery schedule aligned with job completion

---

## Notifications and Alerts

### Email/WhatsApp Notifications

#### 1. Tailor Assignment Notification

**Trigger**: When Tailoring Job Card is submitted (status = "Assigned")  
**Recipient**: Assigned Tailor  
**Content**:
```
Subject: New Tailoring Job Assigned - Job Card #{job_card_number}

Dear {tailor_name},

You have been assigned a new tailoring job.

Job Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Job Card Number: {job_card_number}
Customer: {customer_name}
Project: {project_name}

Expected Start Date: {expected_start_date}
Expected End Date: {expected_end_date}
Expected Duration: {expected_duration_days} days

Tailoring Charge: ₹{tailoring_charge}
Travelling Charge: ₹{travelling_charge}
Total Cost: ₹{total_tailoring_cost}

Materials Required:
{material_list}

Special Instructions:
{special_instructions}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please review the job details and confirm your availability.

View Job Card: {job_card_url}

Thank you!
Fabric Sense Team
```

**WhatsApp Template**:
```
🧵 *New Tailoring Job Assigned!*

Dear {tailor_name},

📋 *Job Card:* {job_card_number}
👤 *Customer:* {customer_name}

📅 *Start Date:* {expected_start_date}
📅 *End Date:* {expected_end_date}
⏱️ *Duration:* {expected_duration_days} days

💰 *Tailoring Charge:* ₹{tailoring_charge}
🚗 *Travel Charge:* ₹{travelling_charge}
💵 *Total:* ₹{total_tailoring_cost}

📦 *Materials:* {material_count} items

View details: {short_url}

Thank you! ✨
```

#### 2. Job Start Notification

**Trigger**: When job status changes to "Started" (actual_start_date is set)  
**Recipient**: Salesperson, Manager  
**Content**:
```
Subject: Tailoring Job Started - Job Card #{job_card_number}

Tailoring work has started for Job Card #{job_card_number}.

Job Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Customer: {customer_name}
Tailor: {tailor_name}
Actual Start Date: {actual_start_date}
Expected Completion: {expected_end_date}

Materials Consumed:
{material_list}

Stock Entry: {stock_entry_reference}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Materials have been issued and stock has been updated.

View Job Card: {job_card_url}
```

#### 3. Job Completion Notification

**Trigger**: When job status changes to "Completed" (actual_end_date is set)  
**Recipient**: Salesperson, Manager, Customer  
**Content**:

**To Salesperson/Manager**:
```
Subject: Tailoring Job Completed - Job Card #{job_card_number}

Tailoring work has been completed for Job Card #{job_card_number}.

Job Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Customer: {customer_name}
Tailor: {tailor_name}

Expected End Date: {expected_end_date}
Actual End Date: {actual_end_date}
Actual Duration: {actual_duration_days} days
Delay: {delay_days} days

Tailoring Cost: ₹{total_tailoring_cost}
Tailor Payment Status: {tailor_payment_status}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
- Perform quality check
- Create Sales Invoice
- Process tailor payment

View Job Card: {job_card_url}
```

**To Customer**:
```
Subject: Your Order is Ready! - Fabric Sense

Dear {customer_name},

Great news! Your tailoring work has been completed and is ready for delivery.

Order Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project: {project_name}
Completion Date: {actual_end_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We will contact you shortly to arrange delivery.

Thank you for choosing Fabric Sense!

Best regards,
Fabric Sense Team
```

**WhatsApp Template for Customer**:
```
✅ *Your Order is Ready!*

Dear {customer_name},

Your tailoring work has been completed! 🎉

📦 *Project:* {project_name}
✅ *Completed:* {actual_end_date}

We'll contact you soon to arrange delivery.

Thank you for choosing Fabric Sense! ✨
```

#### 4. Delay Alert Notification

**Trigger**: When current date > expected_end_date and status != "Completed"  
**Recipient**: Salesperson, Manager, Tailor  
**Content**:
```
Subject: ALERT: Tailoring Job Delayed - Job Card #{job_card_number}

⚠️ DELAY ALERT ⚠️

Job Card #{job_card_number} is delayed.

Job Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Customer: {customer_name}
Tailor: {tailor_name}

Expected End Date: {expected_end_date}
Current Date: {current_date}
Delay: {delay_days} days

Current Status: {job_status}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please take immediate action to complete the job.

View Job Card: {job_card_url}
```

#### 5. Quality Check Notification

**Trigger**: When quality check is completed  
**Recipient**: Salesperson, Manager, Tailor (if failed)  
**Content**:
```
Subject: Quality Check {status} - Job Card #{job_card_number}

Quality check has been completed for Job Card #{job_card_number}.

Quality Check Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: {quality_check_status}
Checked By: {quality_checked_by}
Check Date: {quality_check_date}

Remarks:
{quality_remarks}

{rework_info}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View Job Card: {job_card_url}
```

---

## Reference Documents

- [Tailoring Sheet Creation Guide](./tailoring_sheet_creation.md)
- [Material Request Creation Guide](./material_request_creation.md)
- [Measurement Sheet Creation Guide](./measurement_sheet_creation.md)
- [Case II Implementation](../case-ii-implementation.md)
- [Overview](../overview.md)

---

## Appendix

### Sample Job Card Data

**Example 1: Simple Curtain Tailoring**

```
Job Card Number: TJC-2024-0001
Customer: John Doe
Project: Living Room Curtains
Tailor: Ramesh Kumar

Expected Start Date: 2024-12-10
Expected End Date: 2024-12-15
Expected Duration: 5 days

Tailoring Charge: ₹2,500
Travelling Charge: ₹500
Total Cost: ₹3,000

Materials:
- Premium Linen Fabric: 15 meters
- Satin Lining: 15 meters
- Lead Rope: 60 meters
- French Pleat Tape: 10 meters

Special Instructions:
- Customer prefers tight pleats
- Ensure lining is properly attached
- Double-check measurements before cutting
```

**Example 2: Complex Multi-Room Project**

```
Job Card Number: TJC-2024-0002
Customer: ABC Corporation
Project: Office Curtains - 3 Floors
Tailor: Suresh Tailors

Expected Start Date: 2024-12-20
Expected End Date: 2025-01-05
Expected Duration: 16 days

Tailoring Charge: ₹25,000
Travelling Charge: ₹2,000
Total Cost: ₹27,000

Materials:
- Blackout Fabric: 200 meters
- Thermal Lining: 200 meters
- Motorized Track System: 50 sets
- Various accessories

Special Instructions:
- Fire-retardant treatment required
- All curtains must be identical
- Coordinate with site supervisor for installation
- Quality check mandatory for each floor
```

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Author**: Fabric Sense Development Team
