# Measurement Sheet & Measurement Detail - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Measurement Sheet Doctype](#measurement-sheet-doctype)
3. [Measurement Detail Doctype](#measurement-detail-doctype)
4. [Product Types & Calculations](#product-types--calculations)
5. [Business Logic & Validations](#business-logic--validations)
6. [Technical Implementation](#technical-implementation)
7. [Usage Examples](#usage-examples)
8. [Integration Points](#integration-points)

---

## Overview

The **Measurement Sheet** and **Measurement Detail** doctypes form the core of the Fabric Sense application's measurement and pricing system. They work together to:

- Capture customer window furnishing measurements
- Calculate fabric quantities and pricing automatically
- Support multiple product types (Window Curtains, Roman Blinds, Blinds, Tracks/Rods)
- Manage tailor assignments for on-site measurements
- Track approval workflows
- Include service charges (stitching/fitting) in row totals

### Key Features
- **Automatic Calculations**: Fabric quantities, amounts, and totals are calculated automatically
- **Product Type Support**: Handles 4 different product types with specific logic for each
- **Dynamic Field Visibility**: Fields show/hide based on product type selection
- **Item Group Filtering**: Smart item selection based on product requirements
- **Stock Availability Check**: Built-in functionality to check stock for all items
- **Approval Workflow**: Status-based workflow (Draft → Customer Approval Pending → Approved/Rejected)

---

## Measurement Sheet Doctype

### Purpose
The Measurement Sheet is the parent doctype that captures all necessary information for a customer's window furnishing order, including customer details, measurement method, tailor assignments, and summary calculations.

### Field Structure

#### Basic Information Section

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `naming_series` | Select | Auto-naming series | ✅ Yes | Format: `MS-.YYYY.-.####` (e.g., MS-2025-0001) |
| `customer` | Link (Customer) | Reference to customer | ✅ Yes | Links to ERPNext Customer doctype |
| `project` | Link (Project) | Reference to project | ❌ No | Optional project linkage |
| `measurement_date` | Date | Date when measurements were taken | ✅ Yes | Defaults to current date |
| `status` | Select | Document status | ❌ No | Options: `Draft`, `Customer Approval Pending`, `Approved`, `Rejected` (Default: `Draft`) |
| `measurement_method` | Select | How measurements are obtained | ✅ Yes | Options: `Customer Provided`, `Contractor Assigned` |

#### Tailor Assignment Section (Conditional)
*Visible only when `measurement_method = "Contractor Assigned"`*

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `assigned_contractor` | Link (Employee) | Assigned contractor/tailor | Conditional | Required when measurement_method is "Contractor Assigned" |
| `expected_measurement_date` | Date | Expected completion date | Conditional | Required when measurement_method is "Contractor Assigned" |
| `site_visit_required` | Check | Whether site visit is needed | ❌ No | Default: `0` (unchecked) |
| `visiting_charge` | Currency | Additional charge for site visit | Conditional | Required when `site_visit_required = 1` |
| `actual_measurement_date` | Date | Actual completion date | ❌ No | Read-only, auto-updated |

#### Measurement Details Section

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `measurement_details` | Table | Child table of measurement items | ✅ Yes | Links to `Measurement Detail` doctype |

#### Summary Section

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `total_amount` | Currency | Sum of all measurement detail amounts | ❌ No | **Auto-calculated**, Read-only |
| `rejection_reason` | Text | Reason for rejection | Conditional | Visible when `status = "Rejected"` |

### Status Workflow

```
Draft
  ↓
Customer Approval Pending
  ↓
Approved / Rejected
```

**Status Descriptions:**
- **Draft**: Initial state, can be edited and deleted
- **Customer Approval Pending**: Submitted for customer review, read-only
- **Approved**: Customer approved, ready for Sales Order creation
- **Rejected**: Customer rejected, requires rejection reason

### Server-Side Implementation (`measurement_sheet.py`)

#### Key Methods

**`validate()`**
- Validates tailor assignment fields
- Validates measurement details table
- Calculates totals

**`validate_tailor_assignment()`**
- Ensures `assigned_contractor` is set when `measurement_method = "Contractor Assigned"`
- Ensures `expected_measurement_date` is set
- Validates `visiting_charge` when `site_visit_required = 1`

**`validate_measurement_details()`**
- Ensures at least one measurement detail row exists
- Validates each row based on product type

**`calculate_totals()`**
- Sums all amounts from measurement details into `total_amount`
- Adds `visiting_charge` (if any) on top of the summed child amounts

**`before_save()`**
- No-op; totals are already calculated during validation

### Client-Side Implementation (`measurement_sheet.js`)

#### Key Features

**Dynamic Field Requirements**
- Makes `assigned_contractor` and `expected_measurement_date` mandatory when `measurement_method = "Contractor Assigned"`
- Makes `visiting_charge` mandatory when `site_visit_required = 1`
- Makes `rejection_reason` mandatory when `status = "Rejected"`

**Real-Time Calculations**
- Debounced calculation of totals (50ms delay)
- Recalculates when:
  - Measurement detail amounts change
  - Visiting charge or site visit flag change (totals = child `amount` sum + visiting_charge)

**Stock Availability Check**
- Custom button: "Check Stock Availability"
- Batch queries stock for all items in all measurement detail rows
- Shows insufficient stock items with required vs available quantities

**Item Filters**
- Sets up item group filters for child table fields:
  - `fabric_selected`: Main Fabric, Sheer Fabric
  - `lining`: Lining
  - `lead_rope`: Lead Rope Items
  - `track_rod`: Tracks, Rods, Tracks & Rods
  - `selection`: Blinds Items

---

## Measurement Detail Doctype

### Purpose
The Measurement Detail is a child table doctype (istable: true) that captures individual measurement items within a Measurement Sheet. Each row represents one product/item with its dimensions, materials, and calculated pricing.

### Field Structure

#### Basic Information Section

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `area` | Link (Area) | Area where item will be installed | ✅ Yes | Links to Area master (e.g., "Living Room", "Bedroom") |
| `product_type` | Select | Type of product | ✅ Yes | Options: `Window Curtains`, `Roman Blinds`, `Blinds`, `Tracks/Rods` |
| `layer` | Select | Layer type | Conditional | Visible for Window Curtains & Roman Blinds. Options: `Front`, `Back`, `Main`, `Sheer` |
| `pattern` | Link (Pattern) | Pattern reference | Conditional | Visible for Window Curtains & Roman Blinds. Links to Pattern master |
| `design` | Data | Design description | Conditional | Visible only for Tracks/Rods |

#### Dimensions Section

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `width` | Float | Width in inches | ✅ Yes | Required for all product types |
| `height` | Float | Height in inches | Conditional | Required for all except Tracks/Rods |
| `panels` | Int | Number of panels | Conditional | Visible for Window Curtains & Roman Blinds. Default: `1` |
| `adjust` | Float | Extra fabric adjustment | Conditional | Visible for Window Curtains & Roman Blinds |
| `square_feet` | Float | Calculated square footage | Conditional | **Auto-calculated**, Read-only. Visible for Roman Blinds & Blinds. Formula: `(width × height) / 144` |

#### Items Section

**Fabric Fields** (Visible for Window Curtains & Roman Blinds)

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `fabric_selected` | Link (Item) | Selected fabric item | Conditional | Required for Window Curtains & Roman Blinds. Filtered to Main Fabric/Sheer Fabric item groups |
| `fabric_qty` | Float | Fabric quantity | Conditional | **Auto-calculated**, Read-only |
| `fabric_rate` | Currency | Fabric rate per unit | Conditional | Auto-filled from item's standard_rate |
| `fabric_amount` | Currency | Fabric total amount | Conditional | **Auto-calculated**, Read-only. Formula: `fabric_qty × fabric_rate` |

**Lining Fields** (Visible for Window Curtains & Roman Blinds)

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `lining` | Link (Item) | Lining item | Conditional | Filtered to Lining item group |
| `lining_qty` | Float | Lining quantity | Conditional | **Auto-calculated**, Read-only. Same as fabric_qty |
| `lining_rate` | Currency | Lining rate per unit | Conditional | Auto-filled from item's standard_rate |
| `lining_amount` | Currency | Lining total amount | Conditional | **Auto-calculated**, Read-only. Formula: `lining_qty × lining_rate` |

**Lead Rope Section** (Visible only for Window Curtains)

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `lead_rope` | Link (Item) | Lead rope item | Conditional | Filtered to Lead Rope Items item group |
| `lead_rope_qty` | Float | Lead rope quantity | Conditional | **Auto-calculated**. Formula: `panels × 1.5` |
| `lead_rope_rate` | Currency | Lead rope rate per unit | Conditional | Auto-filled from item's standard_rate |
| `lead_rope_amount` | Currency | Lead rope total amount | Conditional | **Auto-calculated**, Read-only. Formula: `lead_rope_qty × lead_rope_rate` |

**Hardware Section**

**Track/Rod Fields** (Visible only for Window Curtains)

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `track_rod` | Link (Item) | Track/Rod item | Conditional | Filtered to Tracks/Rods item groups |
| `track_rod_qty` | Float | Track/Rod quantity | Conditional | **Auto-calculated**. Formula: `(width / 12) × 2` |
| `track_rod_rate` | Currency | Track/Rod rate per unit | Conditional | Auto-filled from item's standard_rate |
| `track_rod_amount` | Currency | Track/Rod total amount | Conditional | **Auto-calculated**, Read-only. Formula: `track_rod_qty × track_rod_rate` |

**Selection Field** (Visible only for Blinds)

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `selection` | Link (Item) | Blinds item selection | Conditional | Required for Blinds. Filtered to Blinds Items item group. Amount added from item's standard_rate |

#### Service Charges Section

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `stitching_pattern` | Link (Item) | Stitching pattern item | Conditional | Visible for Window Curtains & Roman Blinds. Filtered to Stitching item group |
| `stitching_charge` | Currency | Stitching charge | Conditional | Auto-filled from item rate; editable |
| `fitting_type` | Link (Item) | Fitting type item | ❌ No | Filtered to Fitting item group |
| `fitting_charge` | Currency | Fitting charge | ❌ No | Manual/auto (rate fetched on select) |

#### Total Amount

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `amount` | Currency | Total row amount | ❌ No | **Auto-calculated**, Read-only. Sum of item amounts + service charges; Blinds add `selection` rate |

#### Memo Section

| Field Name | Type | Description | Mandatory | Notes |
|------------|------|-------------|-----------|-------|
| `special_instructions` | Text Editor | Row-level instructions | ❌ No | Free-form notes for production |

### Server-Side Implementation (`measurement_detail.py`)

#### Key Methods

**`validate()`**
- Calculates all amounts (including service charges)
- Calculates square feet
- Calculates fabric/lining quantities
- Calculates lead rope and track/rod quantities

**`calculate_square_feet()`**
- For Roman Blinds and Blinds: `square_feet = (width × height) / 144`
- Sets to 0 if width or height missing

**`calculate_fabric_quantities()`**
- **Window Curtains**: `fabric_qty = ((height + 16) × panels) / 38 + adjust`
- **Roman Blinds/Blinds**: `fabric_qty = square_feet`
- Also sets `lining_qty = fabric_qty` (same value)

**`calculate_amounts()`**
- Calculates `fabric_amount = fabric_qty × fabric_rate`
- Calculates `lining_amount = lining_qty × lining_rate`
- Calculates `lead_rope_amount = lead_rope_qty × lead_rope_rate`
- Calculates `track_rod_amount = track_rod_qty × track_rod_rate`
- Includes `stitching_charge` and `fitting_charge` in total
- Calculates total `amount` = sum of all item amounts + service charges
- For Blinds: adds `selection` rate (Item Price selling > Item.standard_rate fallback)

### Client-Side Implementation (`measurement_detail.js`)

#### Key Features

> Note: All client-side handlers for Measurement Detail now live inside `measurement_sheet.js`. This file is intentionally empty except for a note explaining the relocation.

---

## Product Types & Calculations

### 1. Window Curtains

**Visible Fields:**
- Area, Product Type, Layer, Pattern
- Width, Height, Panels, Adjust
- Fabric Selected, Fabric Qty (auto), Fabric Rate, Fabric Amount (auto)
- Lining, Lining Qty (auto), Lining Rate, Lining Amount (auto)
- Lead Rope, Lead Rope Qty (auto), Lead Rope Rate, Lead Rope Amount (auto)
- Track/Rod, Track/Rod Qty (auto), Track/Rod Rate, Track/Rod Amount (auto)
- Stitching Pattern, Stitching Charge
- Fitting Type, Fitting Charge
- Amount (auto)

**Calculations:**
```
fabric_qty = ((height + 16) × panels) / 38 + adjust
lining_qty = fabric_qty
lead_rope_qty = panels × 1.5
track_rod_qty = (width / 12) × 2

fabric_amount = fabric_qty × fabric_rate
lining_amount = lining_qty × lining_rate
lead_rope_amount = lead_rope_qty × lead_rope_rate
track_rod_amount = track_rod_qty × track_rod_rate
stitching_charge = user / item rate
fitting_charge = user / item rate

amount = fabric_amount + lining_amount + lead_rope_amount + track_rod_amount + stitching_charge + fitting_charge
```

**Required Fields:**
- Area, Product Type, Width, Height, Fabric Selected

### 2. Roman Blinds

**Visible Fields:**
- Area, Product Type, Layer, Pattern
- Width, Height, Panels, Square Feet (auto)
- Fabric Selected, Fabric Qty (auto), Fabric Rate, Fabric Amount (auto)
- Lining, Lining Qty (auto), Lining Rate, Lining Amount (auto)
- Stitching Pattern, Stitching Charge
- Fitting Type, Fitting Charge
- Amount (auto)

**Calculations:**
```
square_feet = (width × height) / 144
fabric_qty = square_feet
lining_qty = fabric_qty

fabric_amount = fabric_qty × fabric_rate
lining_amount = lining_qty × lining_rate
stitching_charge = user / item rate
fitting_charge = user / item rate

amount = fabric_amount + lining_amount + stitching_charge + fitting_charge
```

**Required Fields:**
- Area, Product Type, Width, Height, Fabric Selected

### 3. Blinds

**Visible Fields:**
- Area, Product Type
- Width, Height, Square Feet (auto)
- Selection
- Fitting Type, Fitting Charge
- Amount (auto)

**Calculations:**
```
square_feet = (width × height) / 144
amount = selection rate (Item Price → Item.standard_rate) + fitting_charge
```

**Required Fields:**
- Area, Product Type, Width, Height, Selection

### 4. Tracks/Rods

**Visible Fields:**
- Area, Product Type, Design
- Width
- Track/Rod, Track/Rod Qty (auto), Track/Rod Rate, Track/Rod Amount (auto)
- Fitting Type, Fitting Charge
- Amount (auto)

**Calculations:**
```
track_rod_qty = (width / 12) × 2
track_rod_amount = track_rod_qty × track_rod_rate
amount = track_rod_amount + fitting_charge
```

**Required Fields:**
- Area, Product Type, Width, Design

---

## Business Logic & Validations

### Measurement Sheet Validations

#### Mandatory Field Validations
1. `customer` must be selected
2. `measurement_date` must be set
3. `measurement_method` must be selected
4. At least one `measurement_details` row must exist
5. When `measurement_method = "Contractor Assigned"`:
   - `assigned_contractor` is mandatory
   - `expected_measurement_date` is mandatory
6. When `site_visit_required = 1`:
   - `visiting_charge` is mandatory
7. When `status = "Rejected"`:
   - `rejection_reason` is mandatory

#### Business Rule Validations
1. `total_amount` must be >= 0 (sum of child `amount`)
2. Visiting charge is validated when required but not auto-added to `total_amount`

### Measurement Detail Validations

#### Mandatory Field Validations
1. `area` must be selected
2. `product_type` must be selected
3. `width` must be > 0
4. `height` must be > 0 (except for Tracks/Rods)
5. Product-specific requirements:
   - **Window Curtains**: `fabric_selected` is mandatory
   - **Roman Blinds**: `fabric_selected` is mandatory
   - **Blinds**: `selection` is mandatory

#### Calculation Validations
1. Quantities must be >= 0
2. Rates must be >= 0
3. Amounts are auto-calculated and cannot be manually edited

### Field Dependencies

#### Measurement Sheet
- `tailor_assignment_section`: Visible when `measurement_method = "Contractor Assigned"`
- `visiting_charge`: Visible when `measurement_method = "Contractor Assigned" AND site_visit_required = 1`
- `rejection_reason`: Visible when `status = "Rejected"`

#### Measurement Detail
- `layer`, `pattern`: Visible when `product_type IN ["Window Curtains", "Roman Blinds"]`
- `design`: Visible when `product_type = "Tracks/Rods"`
- `height`: Hidden when `product_type = "Tracks/Rods"`
- `panels`, `adjust`: Visible when `product_type IN ["Window Curtains", "Roman Blinds"]`
- `square_feet`: Visible when `product_type IN ["Roman Blinds", "Blinds"]`
- `fabric_selected`, `fabric_qty`, `fabric_rate`, `fabric_amount`: Visible when `product_type IN ["Window Curtains", "Roman Blinds"]`
- `lining`, `lining_qty`, `lining_rate`, `lining_amount`: Visible when `product_type IN ["Window Curtains", "Roman Blinds"]`
- `lead_rope`, `lead_rope_qty`, `lead_rope_rate`, `lead_rope_amount`: Visible when `product_type = "Window Curtains"`
- `track_rod`, `track_rod_qty`, `track_rod_rate`, `track_rod_amount`: Visible when `product_type IN ["Window Curtains", "Tracks/Rods"]`
- `selection`: Visible when `product_type = "Blinds"`
- `stitching_pattern`, `stitching_charge`: Visible when `product_type IN ["Window Curtains", "Roman Blinds"]`
- `fitting_type`, `fitting_charge`: Always visible (generic fitting charge)

---

## Technical Implementation

### Item Group Constants

`measurement_sheet.js` centralizes client logic (child handlers moved from `measurement_detail.js`):

```javascript
const ITEM_GROUPS = {
    FABRIC: ["Main Fabric", "Sheer Fabric"],
    LINING: "Lining",
    LEAD_ROPE: "Lead Rope Items",
    TRACK_ROD: ["Tracks", "Rods", "Tracks & Rods"],
    BLINDS: "Blinds Items",
    STITCHING: "Stitching",
    FITTING: "Fitting"
};
```

### Calculation Flow

#### Measurement Detail Row Calculation Flow

```
User Input (width, height, panels, etc.)
    ↓
Client-side: batch_calculate_row() [debounced 50ms]
    ↓
calculate_square_feet() [if Roman Blinds/Blinds]
    ↓
calculate_fabric_qty() [based on product type]
    ↓
calculate_row_amounts() [all item amounts + service charges + selection (Blinds)]
    ↓
Trigger parent form calculate_totals()
    ↓
Server-side: validate() [recalculates on save]
```

#### Measurement Sheet Total Calculation Flow

```
Measurement Detail amount changes
    ↓
Client-side: calculate_totals() [debounced 50ms]
    ↓
Sum all measurement_details[].amount + visiting_charge (if provided)
    ↓
Server-side: calculate_totals() [validates on save, stores total_amount]
```

### Performance Optimizations

1. **Debouncing**: All calculations use 50ms debounce to batch rapid changes
2. **Rate Caching**: Item rates are cached to avoid repeated database queries
3. **Batch Queries**: Stock availability check uses batch queries for all items
4. **Conditional Calculations**: Only relevant calculations run based on product type

### Error Handling

1. **Server-side**: Uses `frappe.throw()` for validation errors with user-friendly messages
2. **Client-side**: Uses `frappe.msgprint()` for warnings and errors
3. **Item Rate Fetching**: Handles missing items gracefully (returns null, doesn't fail)

---

## Usage Examples

### Sample Test Data (copy/paste friendly)

**Measurement Sheet (parent)**
- naming_series: `MS-.YYYY.-.####`
- customer: `Test Customer`
- project: _blank_
- measurement_date: today
- measurement_method: `Customer Provided`
- status: `Draft`
- site_visit_required: `0`
- visiting_charge: `0`

**Measurement Detail rows**
- Window Curtains: area `Living Room`, product_type `Window Curtains`, layer `Front`, pattern `Classic Pleat`, width `120`, height `84`, panels `2`, adjust `0.5`, fabric_selected `Main Fabric 1`, fabric_rate `25`, lining `Lining 1`, lining_rate `12`, lead_rope `Lead Rope 1`, lead_rope_rate `3`, track_rod `Track 1`, track_rod_rate `5`, stitching_pattern `Stitch Style 1`, stitching_charge `30`, fitting_type `Fitting 1`, fitting_charge `20`
- Roman Blinds: area `Bedroom`, product_type `Roman Blinds`, layer `Main`, pattern `Plain`, width `60`, height `48`, panels `1`, adjust `0`, fabric_selected `Main Fabric 2`, fabric_rate `22`, lining `Lining 1`, lining_rate `12`, stitching_pattern `Stitch Style 1`, stitching_charge `25`, fitting_type `Fitting 1`, fitting_charge `15`
- Blinds: area `Study`, product_type `Blinds`, width `50`, height `50`, selection `Blind Item 1`, fitting_type `Fitting 1`, fitting_charge `10`
- Tracks/Rods: area `Hallway`, product_type `Tracks/Rods`, design `Single Track`, width `144`, track_rod `Track 2`, track_rod_rate `6`, fitting_type `Fitting 2`, fitting_charge `18`

### Example 1: Creating a Window Curtains Measurement Sheet

**Step 1: Create Measurement Sheet**
1. Navigate to Measurement Sheet list
2. Click "New"
3. Fill in:
   - Customer: "ABC Corp"
   - Measurement Date: Today
   - Measurement Method: "Customer Provided"
   - Status: "Draft"

**Step 2: Add Measurement Detail**
1. Click "Add Row" in Measurement Details table
2. Fill in:
   - Area: "Living Room"
   - Product Type: "Window Curtains"
   - Layer: "Front"
   - Pattern: "French Pleated"
   - Width: 120 (inches)
   - Height: 84 (inches)
   - Panels: 2
   - Adjust: 0.5
   - Fabric Selected: "Premium Cotton Fabric"
   - Lining: "Blackout Lining"
   - Lead Rope: "Standard Lead Rope"
   - Track/Rod: "Aluminum Track"

**Step 3: System Calculations**
- Fabric Qty: `((84 + 16) × 2) / 38 + 0.5 = 5.76` meters
- Lining Qty: `5.76` meters (same as fabric)
- Lead Rope Qty: `2 × 1.5 = 3` units
- Track/Rod Qty: `(120 / 12) × 2 = 20` units
- Add optional stitching/fitting items to include service charges
- Amounts calculated automatically based on rates

**Step 5: Save and Submit**
- Save the document
- Change status to "Customer Approval Pending"

### Example 2: Creating a Blinds Measurement Sheet

**Step 1: Create Measurement Sheet**
- Similar to Example 1

**Step 2: Add Measurement Detail**
- Area: "Bedroom"
- Product Type: "Blinds"
- Width: 60 (inches)
- Height: 48 (inches)
- Selection: "Venetian Blinds - White"

**Step 3: System Calculations**
- Square Feet: `(60 × 48) / 144 = 20` sq ft
- Amount: Item's standard_rate (e.g., $150)

### Example 3: Contractor Assigned Measurement

**Step 1: Create Measurement Sheet**
- Measurement Method: "Contractor Assigned"
- Assigned Contractor: "John Tailor"
- Expected Measurement Date: Next week
- Site Visit Required: ✅ Checked
- Visiting Charge: $50

**Step 2: Add Measurement Details**
- Same as Example 1

**Step 3: System Calculations**
- `total_amount` sums child rows; visiting charge is tracked separately

---

## Integration Points

### 1. Customer Integration
- Links to ERPNext Customer doctype
- Customer details auto-populate

### 2. Project Integration
- Optional linkage to Project doctype
- Useful for project-based orders

### 3. Item Master Integration
- All item selections link to Item master
- Rates fetched from Item.standard_rate
- Item groups used for filtering:
  - Main Fabric, Sheer Fabric
  - Lining
  - Lead Rope Items
  - Tracks, Rods, Tracks & Rods
  - Blinds Items

### 4. Area Master Integration
- Links to Area doctype
- Areas represent installation locations (e.g., "Living Room", "Bedroom")

### 5. Pattern Master Integration
- Links to Pattern doctype
- Used for Window Curtains and Roman Blinds

### 6. Employee Integration
- `assigned_contractor` links to Employee doctype
- Used for contractor/tailor assignments

### 7. Stock Integration
- Stock availability check queries Bin doctype
- Shows available quantities vs required quantities

### 8. Sales Order Integration (Future)
- Approved Measurement Sheets can create Sales Orders
- Measurement details transfer to Sales Order items

---

## Troubleshooting

### Common Issues

**Issue: Calculations not updating**
- **Solution**: Check browser console for JavaScript errors
- Ensure all required fields are filled
- Try refreshing the form

**Issue: Item not appearing in dropdown**
- **Solution**: Verify item's Item Group matches the filter
- Check item is not disabled
- Ensure item exists in Item master

**Issue: Amount showing as 0**
- **Solution**: Verify item has a standard_rate set
- Check quantities are calculated correctly
- Ensure rates are filled

**Issue: Validation errors on save**
- **Solution**: Check all mandatory fields are filled
- Verify product type specific requirements
- Check status-dependent field requirements

---

## Best Practices

1. **Always verify measurements** before saving
2. **Use descriptive area names** for easy identification
3. **Add special instructions** for any custom requirements
4. **Check stock availability** before finalizing orders
5. **Review calculated amounts** before submitting for approval
6. **Use appropriate product types** to ensure correct calculations
7. **Keep item master updated** with correct rates and item groups

---

## Version History

- **v1.1** (9 December 2025): Service charge + field cleanup
  - Added stitching/fitting fields to Measurement Detail and totals
  - Child JS consolidated into `measurement_sheet.js`; `measurement_detail.js` left as stub
  - Removed discount/net amount fields from Measurement Sheet; totals now sum child rows only
  - Documented visibility rules for Tracks/Rods and service charges
- **v1.0** (December 2024): Initial implementation
  - Basic Measurement Sheet and Measurement Detail doctypes
  - Support for 4 product types
  - Automatic calculations
  - Stock availability check
  - Approval workflow

---

## Support & Contact

For issues, questions, or feature requests, please contact the Fabric Sense development team.

---

**Document Version**: 1.1  
**Last Updated**: 9 December 2025   
**Author**: Fabric Sense Development Team

