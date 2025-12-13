# Tailoring Task - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Task Doctype Customization](#task-doctype-customization)
3. [Status Workflow & Automation](#status-workflow--automation)
4. [Business Logic & Validations](#business-logic--validations)
5. [Technical Implementation](#technical-implementation)
6. [Usage Examples](#usage-examples)
7. [Testing Steps](#testing-steps)
8. [Integration Points](#integration-points)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The **Tailoring Task** is a customized ERPNext Task doctype that automates the tailoring workflow from start to completion. It integrates with Tailoring Sheets, Material Requests, Stock Entries, and Services to streamline contractor assignments, material issuance, and payment calculations.

### Key Features
- **Contractor entry**: Contractor is manually selected on the Task (no longer auto-filled from Tailoring Sheet)
- **Service Rate Calculation**: Automatically calculates service charges based on contractor and service
- **Stock Entry Automation**: Opens Material Issue Stock Entry form when tailoring starts
- **Date Tracking**: Automatically sets actual start and end dates based on status changes
- **Charge Calculations**: Calculates service charge, travelling charge, and total contractor amount
- **Status-Based Automation**: Different actions trigger based on Task status (Open → Working → Completed)

---

## Task Doctype Customization

### Purpose
The Task doctype has been customized with additional fields to support the tailoring workflow. These fields are added to the standard ERPNext Task doctype through Customize Form.

### Custom Field Structure

#### Service Details Section

**Left Column:**

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `tailoring_sheet` | Link (Tailoring Sheet) | Reference to Tailoring Sheet | ❌ No | Links to Tailoring Sheet doctype |
| `custom_assigned_contractor` | Link (Employee) | Assigned contractor/tailor | ❌ No | Auto-filled from Tailoring Sheet |
| `unit` | Data | Unit of measurement | ❌ No | Optional field |
| `custom_travelling_charge` | Currency | Travel-related costs | ❌ No | Used in total calculation |
| `custom_total_contractor_amount` | Currency | Total payable to contractor | ❌ No | **Auto-calculated**, Read-only |

**Right Column:**

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `custom_service` | Link (Services) | Type of service being provided | ❌ No | Links to Services doctype |
| `custom_service_rate` | Currency | Rate for the specified service | ❌ No | **Auto-calculated**, Read-only |
| `custom_quantity` | Float | Quantity related to the service | ❌ No | Default: 1.0 |
| `custom_service_charge` | Currency | Calculated service charge | ❌ No | **Auto-calculated**, Read-only |

### Standard Task Fields Used

| Field Name | Type | Description | Notes |
|------------|------|-------------|-------|
| `status` | Select | Task status | Options: Open, Working, Completed, etc. |
| `actual_start_date` | Date | Actual start date | **Auto-set** when status changes to Working |
| `actual_end_date` | Date | Actual end date | **Auto-set** when status changes to Completed |
| `subject` | Data | Task subject/description | User-entered |
| `project` | Link (Project) | Reference to project | Optional |

---

## Status Workflow & Automation

### Status Workflow

```
Open
  ↓
Working (Start Tailoring)
  ↓
Completed (Finish Tailoring)
```

### Automation Triggers

#### A. Status Change: Open → Working

**Trigger**: When Task status changes from "Open" to "Working"

**System Actions**:

1. **Set Actual Start Date**
   - Automatically sets `actual_start_date` to current date if field exists and is empty
   - Only sets if the field exists in the Task doctype

2. **Stock Entry Creation (Material Issue)**
   - Checks for existing Material Request with type "Material Issue" linked to the Tailoring Sheet (`custom_tailoring_sheet`) and submitted (docstatus = 1)
   - If found: opens Stock Entry form (Material Issue) with items/qty from the Material Request; links the MR and the Tailoring Sheet
   - If not found: shows a toast; Stock Entry is not opened
   - User must set source warehouse and submit the Stock Entry manually

**Prerequisites**:
- Tailoring Sheet must be linked to the Task
- Material Request with type "Material Issue" must exist and be submitted for the Tailoring Sheet

#### B. Status Change: Working → Completed

**Trigger**: When Task status changes from "Working" to "Completed"

**System Actions**:

1. **Set Actual End Date**
   - Automatically sets `actual_end_date` to current date if field exists

2. **Fetch Service Rate**
   - Fetches service rate from Services doctype
   - Looks up rate for the selected Contractor and Service combination
   - Searches in the Services doctype's `contractors` child table

3. **Calculate Service Charge**
   - Formula: `Service Charge = Service Rate × Quantity`
   - Uses `custom_service_rate` and `custom_quantity` fields

4. **Calculate Total Contractor Amount**
   - Formula: `Total = Service Charge + Travelling Charge`
   - Uses `custom_service_charge` and `custom_travelling_charge` fields

5. **Write Results to Task Fields**
   - `custom_service_rate`: Fetched rate from Services doctype
   - `custom_service_charge`: Calculated service charge
   - `custom_total_contractor_amount`: Total contractor amount

**Prerequisites**:
- Service must be selected (`custom_service`)
- Contractor must be assigned (`custom_assigned_contractor`)
- Contractor must exist in the Services doctype's contractors child table with a rate

#### C. Prefill Logic (Any Status)

**Trigger**: On any Task save (regardless of status)

**System Actions**:

1. **Prefill Service Rate and Charges**
   - If Service and Contractor are both set
   - Automatically fetches service rate and calculates charges
   - Works even when Task status is "Open"

---

## Business Logic & Validations

### Field Dependencies

#### Tailoring Sheet Integration
- `tailoring_sheet`: Links to Tailoring Sheet doctype
- When Tailoring Sheet is selected and has `tailor_assigned`:
  - `custom_assigned_contractor` is auto-filled (if empty)

#### Service Rate Lookup
- Requires both `custom_service` and `custom_assigned_contractor` to be set
- Searches Services doctype for matching contractor in `contractors` child table
- If contractor not found in service, shows warning message and returns 0.0

#### Calculation Logic

**Service Charge Calculation**:
```
If custom_service and custom_assigned_contractor are set:
    service_rate = get_service_rate(service, contractor)
    service_charge = service_rate × (custom_quantity or 1.0)
    total_contractor_amount = service_charge + (custom_travelling_charge or 0.0)
```

**Date Setting**:
- `actual_start_date`: Set when status changes to "Working" (if field exists and is empty)
- `actual_end_date`: Set when status changes to "Completed" (if field exists)

### Validations

#### Server-Side Validations
1. **Tailoring Sheet Existence**: Validates Tailoring Sheet exists before fetching contractor
2. **Service Rate Lookup**: Validates contractor exists in Services doctype before calculating rates
3. **Field Existence**: Checks if fields exist before setting values (prevents AttributeError)

#### Client-Side Validations
1. **Status Change Detection**: Tracks status changes to trigger appropriate actions
2. **Stock Entry Creation**: Validates Material Request exists before opening Stock Entry form

---

## Technical Implementation

### Server-Side Implementation (`task.py`)

#### Key Functions

**`prefill_from_tailoring_sheet_and_service(doc, method=None)`**
- Runs on every Task save (before_save hook)
- Prefills contractor from Tailoring Sheet if empty
- Calculates service rate and charges if service and contractor are set
- Works regardless of Task status

**`handle_status_change_to_working(doc, method=None)`**
- Runs when status changes to "Working"
- Sets actual_start_date if field exists and is empty
- Fetches contractor from Tailoring Sheet
- Triggered by before_save hook

**`handle_status_change_to_completed(doc, method=None)`**
- Runs when status changes to "Completed"
- Sets actual_end_date if field exists
- Fetches service rate and calculates all charges
- Writes results to Task fields

**`get_service_rate(service, contractor)`**
- Fetches service rate from Services doctype
- Searches contractors child table for matching contractor
- Returns rate or 0.0 if not found
- Shows user-friendly error messages

**`get_material_request_items_for_stock_entry(tailoring_sheet)`**
- Whitelisted method for client-side calls
- Finds Material Request (Issue) linked to Tailoring Sheet
- Returns Material Request name and items list
- Used by client script to create Stock Entry

### Client-Side Implementation (`task.js`)

#### Key Features

**Status Change Detection**:
- Tracks status before save
- Detects status change from "Open" to "Working"
- Triggers Stock Entry form opening after save

**Stock Entry Form Creation**:
- Creates new Stock Entry document
- Sets type to "Material Issue"
- Pre-fills items from Material Request
- Links to Material Request
- Navigates user to Stock Entry form

**Error Handling**:
- Shows informative messages if Material Request not found
- Handles missing items gracefully

### Hook Registration (`hooks.py`)

```python
doc_events = {
    "Task": {
        "before_save": [
            "fabric_sense.fabric_sense.py.task.prefill_from_tailoring_sheet_and_service",
            "fabric_sense.fabric_sense.py.task.handle_status_change_to_working",
            "fabric_sense.fabric_sense.py.task.handle_status_change_to_completed"
        ]
    }
}

doctype_js = {
    "Task": "public/js/task.js"
}
```

### Field Name Handling

The implementation tries multiple possible field names for contractor assignment:
- `custom_assigned_contractor` (primary)
- `assigned_contractor` (fallback)
- `custom_contractor` (fallback)

This ensures compatibility with different field naming conventions.

---

## Usage Examples

### Example 1: Creating a Tailoring Task (Open Status)

**Step 1: Create New Task**
1. Navigate to Task list
2. Click "New"
3. Fill in basic information:
   - Subject: "Tailoring for Customer ABC"
   - Project: Select project (optional)
   - Status: "Open"

**Step 2: Link Tailoring Sheet**
1. In Service Details section, select Tailoring Sheet
2. System automatically fetches contractor from Tailoring Sheet (if `tailor_assigned` exists)
3. `custom_assigned_contractor` field is auto-filled

**Step 3: Select Service**
1. Select Service from `custom_service` dropdown
2. If contractor is already set, system automatically:
   - Fetches service rate from Services doctype
   - Calculates service charge = service_rate × quantity
   - Calculates total contractor amount = service_charge + travelling_charge
3. Fields are auto-filled:
   - `custom_service_rate`
   - `custom_service_charge`
   - `custom_total_contractor_amount`

**Step 4: Set Quantity and Travelling Charge**
1. Enter quantity in `custom_quantity` field (default: 1.0)
2. Enter travelling charge if applicable in `custom_travelling_charge`
3. Save the Task
4. Calculations update automatically

### Example 2: Starting Tailoring (Status: Working)

**Step 1: Change Status to Working**
1. Open existing Task with status "Open"
2. Change status to "Working"
3. Save the Task

**Step 2: System Actions (Automatic)**
1. `actual_start_date` is set to current date (if field exists)
2. Contractor is fetched from Tailoring Sheet (if not already set)
3. Stock Entry form opens automatically with:
   - Type: "Material Issue"
   - Purpose: "Material Issue to Tailor"
   - Items pre-filled from Material Request (Issue)

**Step 3: Complete Stock Entry**
1. Review pre-filled items in Stock Entry form
2. Set source warehouse
3. Review quantities
4. Submit the Stock Entry
5. Stock is reduced (Case II rule)

### Example 3: Completing Tailoring (Status: Completed)

**Step 1: Change Status to Completed**
1. Open Task with status "Working"
2. Ensure Service and Contractor are set
3. Change status to "Completed"
4. Save the Task

**Step 2: System Actions (Automatic)**
1. `actual_end_date` is set to current date (if field exists)
2. Service rate is fetched from Services doctype
3. Service charge is calculated: `service_rate × quantity`
4. Total contractor amount is calculated: `service_charge + travelling_charge`
5. All calculated fields are updated:
   - `custom_service_rate`
   - `custom_service_charge`
   - `custom_total_contractor_amount`

**Step 3: Review Results**
1. Check calculated amounts in Service Details section
2. Verify service rate matches Services doctype
3. Verify total contractor amount is correct

---

## Testing Steps

### Test Case 1: Prefill Contractor from Tailoring Sheet

**Prerequisites**:
- Tailoring Sheet exists with `tailor_assigned` field populated
- Task doctype has `tailoring_sheet` and `custom_assigned_contractor` fields

**Steps**:
1. Create new Task
2. Set status to "Open"
3. Select Tailoring Sheet in `tailoring_sheet` field
4. Save the Task
5. **Expected Result**: `custom_assigned_contractor` is auto-filled with contractor from Tailoring Sheet

**Verification**:
- Check `custom_assigned_contractor` field is populated
- Verify contractor matches `tailor_assigned` in Tailoring Sheet

### Test Case 2: Prefill Service Rate and Charges (Open Status)

**Prerequisites**:
- Services doctype exists with service
- Service has contractor in `contractors` child table with rate
- Task has Tailoring Sheet and Service selected

**Steps**:
1. Create new Task
2. Set status to "Open"
3. Select Tailoring Sheet (contractor auto-filled)
4. Select Service in `custom_service` field
5. Set quantity in `custom_quantity` (optional, default: 1.0)
6. Set travelling charge in `custom_travelling_charge` (optional)
7. Save the Task
8. **Expected Result**: 
   - `custom_service_rate` is auto-filled
   - `custom_service_charge` is calculated
   - `custom_total_contractor_amount` is calculated

**Verification**:
- Check `custom_service_rate` matches rate in Services doctype
- Verify `custom_service_charge = service_rate × quantity`
- Verify `custom_total_contractor_amount = service_charge + travelling_charge`

### Test Case 3: Status Change to Working

**Prerequisites**:
- Task exists with status "Open"
- Tailoring Sheet is linked
- Material Request (Issue) exists and is submitted for the Tailoring Sheet

**Steps**:
1. Open Task with status "Open"
2. Change status to "Working"
3. Save the Task
4. **Expected Result**:
   - `actual_start_date` is set to current date (if field exists)
   - Contractor is fetched if not already set
   - Stock Entry form opens automatically
   - Stock Entry has items pre-filled from Material Request

**Verification**:
- Check `actual_start_date` is set
- Verify Stock Entry form opens
- Check Stock Entry items match Material Request items
- Verify Stock Entry type is "Material Issue"
- Verify Stock Entry purpose is "Material Issue to Tailor"

### Test Case 4: Status Change to Completed

**Prerequisites**:
- Task exists with status "Working"
- Service and Contractor are set
- Contractor exists in Services doctype with rate

**Steps**:
1. Open Task with status "Working"
2. Ensure Service and Contractor are set
3. Change status to "Completed"
4. Save the Task
5. **Expected Result**:
   - `actual_end_date` is set to current date (if field exists)
   - `custom_service_rate` is fetched from Services doctype
   - `custom_service_charge` is calculated
   - `custom_total_contractor_amount` is calculated

**Verification**:
- Check `actual_end_date` is set
- Verify `custom_service_rate` matches Services doctype rate
- Verify `custom_service_charge = service_rate × quantity`
- Verify `custom_total_contractor_amount = service_charge + travelling_charge`

### Test Case 5: Stock Entry Creation from Material Request

**Prerequisites**:
- Tailoring Sheet exists
- Material Request (Material Issue) exists and is submitted for the Tailoring Sheet
- Material Request has items

**Steps**:
1. Create Task with Tailoring Sheet linked
2. Change status to "Working"
3. Save the Task
4. **Expected Result**: Stock Entry form opens with:
   - Items from Material Request
   - Quantities matching Material Request
   - Material Request linked
   - `stock_uom`, `conversion_factor`, and `transfer_qty` (Qty as per Stock UOM) set on items

**Verification**:
- Check Stock Entry items count matches Material Request items
- Verify item codes match
- Verify quantities match
- Check Material Request is linked in Stock Entry

### Test Case 6: Service Rate Not Found

**Prerequisites**:
- Task has Service and Contractor set
- Contractor does NOT exist in Services doctype's contractors table

**Steps**:
1. Create Task
2. Select Service
3. Select Contractor (that doesn't exist in Services)
4. Save the Task
5. **Expected Result**: 
   - Warning message displayed
   - `custom_service_rate` = 0.0
   - `custom_service_charge` = 0.0

**Verification**:
- Check for warning message about service rate not found
- Verify calculated fields are 0.0

### Test Case 7: Material Request Not Found

**Prerequisites**:
- Task has Tailoring Sheet linked
- No Material Request (Issue) exists for the Tailoring Sheet

**Steps**:
1. Create Task with Tailoring Sheet
2. Change status to "Working"
3. Save the Task
4. **Expected Result**: 
   - Informative message displayed
   - Stock Entry form does NOT open

**Verification**:
- Check for message about no Material Request found
- Verify Stock Entry form does not open

---

## Integration Points

### 1. Tailoring Sheet Integration
- **Link Field**: `tailoring_sheet` (Link to Tailoring Sheet)
- **Data Fetched**: `tailor_assigned` → `custom_assigned_contractor`
- **Use Case**: Auto-fill contractor when Tailoring Sheet is selected

### 2. Services Doctype Integration
- **Link Field**: `custom_service` (Link to Services)
- **Data Fetched**: Service rate from `contractors` child table
- **Lookup Logic**: Matches contractor in Services.contractors table
- **Use Case**: Calculate service charges based on contractor and service

### 3. Material Request Integration
- **Link**: Material Request linked to Tailoring Sheet via `custom_tailoring_sheet`
- **Filter**: Material Request type = "Material Issue", docstatus = 1 (Submitted)
- **Use Case**: Pre-fill Stock Entry items when tailoring starts

### 4. Stock Entry Integration
- **Type**: Material Issue
- **Purpose**: Material Issue to Tailor
- **Items**: Pre-filled from Material Request
- **Use Case**: Issue materials to tailor when tailoring starts
- **Item fields set**: `stock_uom`, `conversion_factor`, `transfer_qty` (Qty as per Stock UOM) to satisfy mandatory UOM requirements

### 5. Employee Integration
- **Link Field**: `custom_assigned_contractor` (Link to Employee)
- **Use Case**: Track which contractor/tailor is assigned to the task

### 6. Project Integration
- **Link Field**: `project` (Link to Project)
- **Use Case**: Group tasks by project

---

## Troubleshooting

### Common Issues

**Issue: Contractor not being prefilled from Tailoring Sheet**

**Possible Causes**:
- Tailoring Sheet doesn't have `tailor_assigned` field populated
- Field name mismatch (check if using `custom_assigned_contractor`, `assigned_contractor`, or `custom_contractor`)
- Tailoring Sheet not properly linked

**Solutions**:
1. Verify Tailoring Sheet has `tailor_assigned` field set
2. Check Error Log for field name issues
3. Verify `tailoring_sheet` field is correctly linked
4. Check if contractor field already has a value (won't overwrite)

**Issue: Service rate showing as 0.0**

**Possible Causes**:
- Contractor not found in Services doctype's contractors table
- Service not selected
- Contractor not selected

**Solutions**:
1. Verify Service is selected
2. Verify Contractor is selected
3. Check Services doctype has the contractor in `contractors` child table
4. Verify contractor has a rate set in Services doctype
5. Check Error Log for detailed error messages

**Issue: Stock Entry form not opening**

**Possible Causes**:
- No Material Request (Issue) exists for Tailoring Sheet
- Material Request is not submitted
- Material Request has no items

**Solutions**:
1. Verify Material Request exists for the Tailoring Sheet
2. Check Material Request type is "Issue"
3. Verify Material Request is submitted (docstatus = 1)
4. Check Material Request has items
5. Review message displayed for specific issue

**Issue: Actual start/end date not being set**

**Possible Causes**:
- Field doesn't exist in Task doctype
- Field already has a value (start date only)

**Solutions**:
1. Verify `actual_start_date` and `actual_end_date` fields exist in Task doctype
2. For start date: Check if field already has a value (won't overwrite)
3. Check Error Log for any errors

**Issue: Calculations not updating**

**Possible Causes**:
- Service or Contractor not set
- Quantity or travelling charge not set (defaults used)
- Service rate lookup failing

**Solutions**:
1. Verify Service and Contractor are both set
2. Check quantity is set (defaults to 1.0)
3. Verify travelling charge is set if needed (defaults to 0.0)
4. Check Error Log for service rate lookup errors
5. Save the Task to trigger recalculation

**Issue: AttributeError on save**

**Possible Causes**:
- Field doesn't exist in Task doctype
- Field name mismatch

**Solutions**:
1. Verify all custom fields exist in Task doctype
2. Check field names match exactly (case-sensitive)
3. Review Error Log for specific field causing issue
4. Ensure fields are added through Customize Form

---

## Best Practices

1. **Always link Tailoring Sheet** before changing status to "Working"
2. **Set Service and Contractor** before changing status to "Completed" for accurate calculations
3. **Verify Material Request exists** before starting tailoring to ensure Stock Entry can be created
4. **Review calculated amounts** before finalizing the Task
5. **Check Services doctype** to ensure contractor rates are up-to-date
6. **Set quantity and travelling charge** if different from defaults
7. **Verify Stock Entry** before submitting to ensure correct warehouse and quantities
8. **Keep Tailoring Sheet updated** with correct contractor assignments

---

## Version History

- **v1.0** (December 2025): Initial implementation
  - Task doctype customization with Service Details fields
  - Status-based automation (Open → Working → Completed)
  - Contractor prefilling from Tailoring Sheet
  - Service rate lookup and charge calculations
  - Stock Entry automation for material issuance
  - Date tracking (actual start/end dates)

---

## Support & Contact

For issues, questions, or feature requests, please contact the Fabric Sense development team.

---

**Document Version**: 1.0  
**Last Updated**: December 2025  
**Author**: Fabric Sense Development Team
