# Tailoring Sheet Creation - Implementation Guide

## Overview
The Tailoring Sheet is a specialized doctype in the Fabric Sense application that serves as a bridge between the Measurement Sheet and the actual tailoring process. It is an exact copy of the Measurement Sheet doctype structure with additional adjustment fields where tailors can record measurement changes or corrections needed during the tailoring process.

### Key Characteristics
- **Exact Copy**: The Tailoring Sheet mirrors all fields from the Measurement Sheet doctype
- **Auto-Fetch**: When a Measurement Sheet is selected, all values are automatically fetched and populated
- **Manual Adjustments**: Adjustment fields remain empty after fetching and must be entered manually by users
- **Dynamic Calculations**: Final quantities and amounts are calculated automatically based on adjustments

## Doctype: Tailoring Sheet

### Purpose
- Create a working copy of the approved Measurement Sheet for tailoring purposes
- Allow salespersons to make adjustments to measurements based on practical requirements
- Track adjustments separately from original measurements
- Serve as the basis for Material Request creation
- Maintain traceability between measurement and tailoring phases
- Calculate final material requirements including adjustments

---

## Field Structure

### Basic Information Fields

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `naming_series` | Data | Auto-naming series (e.g., TS-.YYYY.-.####) | Yes |
| `measurement_sheet` | Link (Measurement Sheet) | Reference to source measurement sheet | Yes |
| `customer` | Link (Customer) | Reference to the customer | Yes |
| `project` | Link (Project) | Reference to the project | Yes |
| `sales_order` | Link (Sales Order) | Reference to the sales order | No |
| `date` | Date | Date when tailoring sheet was created | Yes |
| `status` | Select | Draft, In Progress, Completed | Yes |


### Measurement Details (Child Table)

**Child Table Name:** `measurement_details`

This table is an exact copy of the measurement sheet details and is read-only.

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `area` | Data | Area where treatment will be installed | Yes |
| `product_type` | Select | Window Curtains, Roman Blinds, Blinds, Tracks/Rods | Yes |
| `layer` | Select | Front, Back | Conditional |
| `pattern` | Link (Pattern) | Pattern type | Conditional |
| `width` | Float | Width in inches | Conditional |
| `height` | Float | Height in inches | Conditional |
| `panels` | Int | Number of panels | Conditional |
| `adjust` | Float | Original adjustment value | No |
| `quantity` | Float | Original calculated quantity | Yes |
| `fabric_type` | Link (Item) | Fabric item reference | Conditional |
| `lead_rope` | Link (Item) | Lead rope item | Conditional |
| `lining` | Link (Item) | Lining item reference | Conditional |
| `track_rod_type` | Link (Item) | Track/Rod type | Conditional |
| `design` | Link (Design) | Design for tracks/rods | Conditional |
| `selection` | Data | Material type or color | Conditional |
| `square_feet` | Float | Original square footage | Auto-calculated |
| `rate` | Currency | Rate per unit | Yes |
| `amount` | Currency | Original amount | Auto-calculated |

.....etc.

---

## Status Workflow

### Status Options
1. **Draft** - Initial state when tailoring sheet is created from measurement sheet
3. **In Progress** - When tailoring work has started
4. **Completed** - When tailoring work is finished

---

## Adjustment Types and Use Cases

### Addition
**When to use:**
- Customer requests additional fabric for extra fullness
- Need extra material for pattern matching
- Additional panels required
- Safety margin for complex patterns

```
---

## Creation Process

### 1️⃣ Data Fetching From Measurement Sheet

The Tailoring Sheet contains a **Measurement Sheet** field (Link field type).

**Auto-Fetch Behavior:**
1. When a Measurement Sheet is selected in the link field
2. All corresponding values are automatically fetched from the selected Measurement Sheet record
3. Fetched values populate all matching fields inside the Tailoring Sheet doctype
4. **Important**: Adjustment fields remain empty even after fetching
5. Users must manually enter adjustment values

**Fields Auto-Populated:**
- Customer
- Project
- All measurement detail rows (area, product_type, width, height, panels, quantity, etc.)
- All item references (fabric_type, lining, track_rod_type, etc.)
- All calculated fields (square_feet, amount, etc.)
- Rate and pricing information

**Fields That Remain Empty:**
- All adjustment-related fields
- Fabric adjustment
- Lining adjustment

### Manual Adjustment Entry
After data is fetched from the Measurement Sheet, users can enter adjustments:

1. Review auto-fetched original measurements
2. Identify items needing adjustments
3. Manually enter adjustment values in the adjustment fields
4. Provide adjustment type and reason
5. System auto-calculates final quantities and amounts
6. Review final material requirements
7. Submit for processing

---

## Calculation Formulas

### 2️⃣ Adjustment Logic

Users can manually enter values in the adjustment fields. The system calculates final quantities based on whether adjustments are provided.

**Formula:**
```
final_qty = original_qty + adjusted_qty
```

**Behavior:**
- If an adjustment value is provided: `final_qty = original_qty + adjusted_qty`
- If there is no adjustment: `final_qty = original_qty`

```

---

## Validation Rules

### Business Logic Validations
1. Tailoring Sheet can only be created from Approved Measurement Sheet
2. Adjusted quantities must be greater than 0
3. Final quantities cannot be negative
---

## Integration Points

### 1. Measurement Sheet Integration
- Tailoring Sheet created from approved Measurement Sheet
- All original measurements copied automatically
- Link maintained for traceability


### 2. Material Request Integration
- "Create Material Request" button available when status = "Completed"
- Material Requests created based on `measurement_details` table
- Separate Material Requests for in-stock and on-order items
- Stock availability checked automatically

---

## Unit Test Case Scenarios

### Test Suite 1: Tailoring Sheet Creation

#### TC-TS-001: Create Tailoring Sheet from Approved Measurement Sheet
**Objective:** Verify that a Tailoring Sheet can be created from an approved Measurement Sheet

**Preconditions:**
- An approved Measurement Sheet exists with status "Approved"
- User has permission to create Tailoring Sheet

**Test Steps:**
1. Navigate to Tailoring Sheet creation form
2. Select an approved Measurement Sheet in the `measurement_sheet` field
3. Verify all fields are auto-populated from the Measurement Sheet
4. Save the Tailoring Sheet

**Expected Results:**
- Tailoring Sheet is created successfully with status "Draft"
- All basic information fields (customer, project, sales_order) are auto-populated
- All measurement details are copied to the child table
- Adjustment fields remain empty
- Original quantities and amounts are preserved

**Test Data:**
- Measurement Sheet: MS-2024-0001 (Status: Approved)
- Expected Customer: CUST-001
- Expected Project: PROJ-001

---

#### TC-TS-002: Prevent Creation from Non-Approved Measurement Sheet
**Objective:** Verify that Tailoring Sheet cannot be created from a non-approved Measurement Sheet

**Preconditions:**
- A Measurement Sheet exists with status "Draft" or "Submitted"

**Test Steps:**
1. Navigate to Tailoring Sheet creation form
2. Attempt to select a non-approved Measurement Sheet
3. Try to save the form

**Expected Results:**
- System displays validation error
- Error message: "Tailoring Sheet can only be created from Approved Measurement Sheet"
- Tailoring Sheet is not created

**Test Data:**
- Measurement Sheet: MS-2024-0002 (Status: Draft)

---

### Test Suite 2: Data Fetching and Auto-Population

#### TC-TS-003: Verify Auto-Fetch of Basic Information
**Objective:** Verify that basic information fields are auto-populated when Measurement Sheet is selected

**Test Steps:**
1. Create new Tailoring Sheet
2. Select Measurement Sheet: MS-2024-0001
3. Verify auto-populated fields

**Expected Results:**
- `customer` field populated with correct customer link
- `project` field populated with correct project link
- `date` field set to current date

**Test Data:**
- Measurement Sheet: MS-2024-0001
- Expected Customer: CUST-001
- Expected Project: PROJ-001

---

#### TC-TS-004: Verify Auto-Fetch of Measurement Details
**Objective:** Verify that all measurement detail rows are copied correctly

**Test Steps:**
1. Create new Tailoring Sheet
2. Select Measurement Sheet with multiple measurement detail rows
3. Verify all rows are copied to `measurement_details` child table

**Expected Results:**
- All rows from source Measurement Sheet are present
- All fields in each row match source values (area, product_type, width, height, panels, etc.)
- Original quantity and amount values are preserved
- Adjustment fields are empty

**Test Data:**
- Measurement Sheet: MS-2024-0001 with 5 measurement detail rows

---

#### TC-TS-005: Verify Adjustment Fields Remain Empty After Fetch
**Objective:** Verify that adjustment fields are not auto-populated

**Test Steps:**
1. Create new Tailoring Sheet
2. Select Measurement Sheet
3. Check all adjustment-related fields

**Expected Results:**
- `fabric_adjustment` is empty
- `lining_adjustment` is empty
- All adjustment fields in child table rows are empty

---

### Test Suite 3: Manual Adjustment Entry

#### TC-TS-006: Add Positive Adjustment to Fabric Quantity
**Objective:** Verify that positive adjustments are calculated correctly

**Preconditions:**
- Tailoring Sheet exists with original fabric quantity = 50 meters

**Test Steps:**
1. Open existing Tailoring Sheet
2. Enter adjustment value: +10 in fabric adjustment field
3. Save the document

**Expected Results:**
- `final_qty` = 60 (50 + 10)
- `final_amount` recalculated based on final_qty and rate

**Test Data:**
- Original Quantity: 50 meters
- Adjustment: +10 meters
- Expected Final Quantity: 60 meters

---

#### TC-TS-007: Add Negative Adjustment to Fabric Quantity
**Objective:** Verify that negative adjustments are calculated correctly

**Preconditions:**
- Tailoring Sheet exists with original fabric quantity = 50 meters

**Test Steps:**
1. Open existing Tailoring Sheet
2. Enter adjustment value: -5 in fabric adjustment field
3. Save the document

**Expected Results:**
- `final_qty` = 45 (50 - 5)
- `final_amount` recalculated based on final_qty and rate
- Document saves successfully

**Test Data:**
- Original Quantity: 50 meters
- Adjustment: -5 meters
- Expected Final Quantity: 45 meters

---

#### TC-TS-008: Prevent Negative Final Quantity
**Objective:** Verify that adjustments resulting in negative final quantities are rejected

**Preconditions:**
- Tailoring Sheet exists with original fabric quantity = 50 meters

**Test Steps:**
1. Open existing Tailoring Sheet
2. Enter adjustment value: -60 in fabric adjustment field
3. Attempt to save the document

**Expected Results:**
- System displays validation error
- Error message: "Final quantities cannot be negative"
- Document is not saved

**Test Data:**
- Original Quantity: 50 meters
- Adjustment: -60 meters
- Expected Final Quantity: -10 (Invalid)

---

#### TC-TS-009: No Adjustment Entered
**Objective:** Verify behavior when no adjustment is provided

**Preconditions:**
- Tailoring Sheet exists with original fabric quantity = 50 meters

**Test Steps:**
1. Open existing Tailoring Sheet
2. Leave adjustment field empty
3. Save the document

**Expected Results:**
- `final_qty` = 50 (same as original_qty)
- `final_amount` = original_amount
- Document saves successfully

**Test Data:**
- Original Quantity: 50 meters
- Adjustment: (empty)
- Expected Final Quantity: 50 meters

---

### Test Suite 4: Calculation Formulas

#### TC-TS-010: Verify Final Quantity Calculation
**Objective:** Verify the formula: final_qty = original_qty + adjusted_qty

**Test Steps:**
1. Create Tailoring Sheet with original_qty = 100
2. Add adjustment = 25
3. Verify calculation

**Expected Results:**
- `final_qty` = 125

**Test Data:**
- Original Quantity: 100
- Adjustment: 25
- Expected Final Quantity: 125

---

#### TC-TS-011: Verify Final Amount Calculation
**Objective:** Verify that final amount is calculated based on final quantity and rate

**Test Steps:**
1. Create Tailoring Sheet with original_qty = 100, rate = 50
2. Add adjustment = 20
3. Verify amount calculation

**Expected Results:**
- `final_qty` = 120
- `final_amount` = 6000 (120 * 50)

**Test Data:**
- Original Quantity: 100
- Rate: 50
- Adjustment: 20
- Expected Final Amount: 6000

---

### Test Suite 5: Status Workflow

#### TC-TS-013: Initial Status is Draft
**Objective:** Verify that newly created Tailoring Sheet has status "Draft"

**Test Steps:**
1. Create new Tailoring Sheet from approved Measurement Sheet
2. Save the document
3. Check status field

**Expected Results:**
- Status = "Draft"

---

#### TC-TS-014: Change Status to In Progress
**Objective:** Verify status can be changed from Draft to In Progress

**Test Steps:**
1. Open Tailoring Sheet with status "Draft"
2. Change status to "In Progress"
3. Save the document

**Expected Results:**
- Status updated to "In Progress"
- Document saves successfully

---

#### TC-TS-015: Change Status to Completed
**Objective:** Verify status can be changed to Completed

**Test Steps:**
1. Open Tailoring Sheet with status "In Progress"
2. Change status to "Completed"
3. Save the document

**Expected Results:**
- Status updated to "Completed"
- "Create Material Request" button becomes available

---

### Test Suite 6: Validation Rules

#### TC-TS-016: Validate Adjusted Quantity Greater Than Zero
**Objective:** Verify that adjusted quantities must be greater than 0

**Test Steps:**
1. Open Tailoring Sheet
2. Enter adjustment resulting in final_qty = 0
3. Attempt to save

**Expected Results:**
- System displays validation error
- Error message: "Adjusted quantities must be greater than 0"
- Document is not saved

---

#### TC-TS-017: Validate Mandatory Fields
**Objective:** Verify that mandatory fields are enforced

**Test Steps:**
1. Create new Tailoring Sheet
2. Leave mandatory fields empty (measurement_sheet, customer, project, date)
3. Attempt to save

**Expected Results:**
- System displays validation errors for each missing mandatory field
- Document is not saved

---

### Test Suite 7: Integration with Material Request

#### TC-TS-018: Create Material Request Button Availability
**Objective:** Verify that "Create Material Request" button is only available when status is "Completed"

**Test Steps:**
1. Open Tailoring Sheet with status "Draft"
2. Check for "Create Material Request" button
3. Change status to "Completed"
4. Check for button again

**Expected Results:**
- Button is not visible when status is "Draft" or "In Progress"
- Button becomes visible when status is "Completed"

---

#### TC-TS-019: Create Material Request from Tailoring Sheet
**Objective:** Verify that Material Request can be created from completed Tailoring Sheet

**Preconditions:**
- Tailoring Sheet exists with status "Completed"
- Measurement details contain items with final quantities

**Test Steps:**
1. Open completed Tailoring Sheet
2. Click "Create Material Request" button
3. Verify Material Request creation

**Expected Results:**
- Material Request(s) created successfully
- Items from measurement_details are transferred to Material Request
- Final quantities are used (not original quantities)
- Separate Material Requests created for in-stock and on-order items

---

### Test Suite 8: Edge Cases and Error Handling

#### TC-TS-020: Handle Empty Measurement Sheet
**Objective:** Verify behavior when selected Measurement Sheet has no measurement details

**Test Steps:**
1. Create Tailoring Sheet
2. Select Measurement Sheet with no measurement detail rows
3. Save the document

**Expected Results:**
- Tailoring Sheet is created
- measurement_details child table is empty
- Warning message displayed: "No measurement details found in selected Measurement Sheet"

---

#### TC-TS-022: Concurrent Editing Prevention
**Objective:** Verify that concurrent edits are handled properly

**Test Steps:**
1. User A opens Tailoring Sheet TS-2024-0001
2. User B opens the same Tailoring Sheet
3. User A makes changes and saves
4. User B attempts to save changes

**Expected Results:**
- System detects concurrent edit
- User B receives notification about document being modified
- User B must refresh to see latest changes

---

### Test Suite 9: Performance and Data Integrity

#### TC-TS-023: Handle Large Measurement Details
**Objective:** Verify system performance with large number of measurement detail rows

**Test Steps:**
1. Create Measurement Sheet with 100+ measurement detail rows
2. Create Tailoring Sheet from this Measurement Sheet
3. Verify all rows are copied
4. Add adjustments to multiple rows
5. Save the document

**Expected Results:**
- All rows copied successfully within acceptable time (< 5 seconds)
- All calculations performed correctly
- No data loss or corruption

---

#### TC-TS-024: Verify Data Integrity After Fetch
**Objective:** Verify that fetched data exactly matches source Measurement Sheet

**Test Steps:**
1. Create Tailoring Sheet from Measurement Sheet MS-2024-0001
2. Compare all fields between Tailoring Sheet and source Measurement Sheet
3. Verify data integrity

**Expected Results:**
- All fetched values exactly match source values
- No data transformation or loss
- Decimal precision maintained for float values
- Currency values maintain precision

---

### Test Suite 10: Traceability and Audit

#### TC-TS-025: Verify Link to Source Measurement Sheet
**Objective:** Verify that link to source Measurement Sheet is maintained

**Test Steps:**
1. Create Tailoring Sheet from Measurement Sheet MS-2024-0001
2. Verify measurement_sheet field contains correct link
3. Click on link to navigate to source document

**Expected Results:**
- measurement_sheet field contains correct link
- Clicking link opens source Measurement Sheet
- Link remains valid after saving

---

#### TC-TS-026: Verify Naming Series
**Objective:** Verify that Tailoring Sheet follows correct naming convention

**Test Steps:**
1. Create multiple Tailoring Sheets
2. Verify naming pattern

**Expected Results:**
- Naming follows pattern: TS-.YYYY.-.####
- Example: TS-2024-0001, TS-2024-0002
- Sequential numbering is maintained

---

## Test Execution Guidelines

### Test Environment Setup
1. Fresh database with sample data
2. Test users with appropriate permissions
3. Sample Measurement Sheets in various statuses
4. Sample Items (fabrics, linings, hardware)

### Test Data Requirements
- At least 5 approved Measurement Sheets
- At least 2 non-approved Measurement Sheets
- Sample customers and projects
- Sample items with stock availability

### Automation Recommendations
- Test Suites 1-7: High priority for automation
- Test Suites 8-10: Medium priority for automation
- Use Frappe's unit test framework for backend tests
- Use Cypress or Selenium for UI tests

### Expected Test Coverage
- Unit Tests: 80%+ code coverage
- Integration Tests: All critical workflows
- UI Tests: All user-facing features

---
### Test data used in dev environment
 Measurement record : MS-2025-0002
 Tailoring sheet : TS-2025-0001

## Reference Documents
- [Measurement Sheet Creation Guide](./measurement_sheet_creation.md)
- [Material Request Creation Guide](./material_request_creation.md)
- [Case II Implementation](../case-ii-implementation.md)
- [Overview](../overview.md)

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Author**: Fabric Sense Development Team
