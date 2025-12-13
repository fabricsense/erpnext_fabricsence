# Sales Order from Measurement Sheet - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [User Guide](#user-guide)
5. [Item Mapping Logic](#item-mapping-logic)
6. [Status Workflow](#status-workflow)
7. [Integration Points](#integration-points)
8. [Testing Guide](#testing-guide)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)
11. [Related Documentation](#related-documentation)

---

## Overview

The **Sales Order from Measurement Sheet** feature enables automatic pre-population of Sales Orders from approved Measurement Sheets. When a Measurement Sheet is approved, users can create a Sales Order with a single click, and the system will automatically populate:

- **Customer** from the Measurement Sheet
- **Items Table** with all items (fabric, lining, lead rope, track/rod, selection, stitching, fitting) from the Measurement Sheet's measurement details
- **Quantities and Rates** for each item
- **Measurement Sheet Link** to maintain traceability
- **Project** (if linked to Measurement Sheet)

### Key Features
- ✅ One-click Sales Order creation from approved Measurement Sheets
- ✅ Automatic customer and item population
- ✅ Support for all product types (Window Curtains, Roman Blinds, Blinds, Tracks/Rods)
- ✅ Service charges (stitching and fitting) as separate item rows
- ✅ Automatic rate fetching for items
- ✅ Pre-population approach (user reviews before saving)
- ✅ Comprehensive error handling and validation

---

## Features

### Automatic Data Population
- Customer details automatically transferred from Measurement Sheet
- All items from measurement details automatically added to Sales Order
- Quantities and rates preserved from Measurement Sheet
- Project linkage maintained (if applicable)

### Product Type Support
- **Window Curtains**: Fabric, lining, lead rope, track/rod, stitching, fitting
- **Roman Blinds**: Fabric, lining, stitching, fitting
- **Blinds**: Selection item, fitting
- **Tracks/Rods**: Track/rod, fitting

### Service Charges
- Stitching charges added as separate item rows (qty = 1)
- Fitting charges added as separate item rows (qty = 1)
- Charges preserved from Measurement Sheet

### Rate Fetching
- Regular items use rates from Measurement Sheet
- Selection items (Blinds) fetch rates from Item Price or Item standard_rate
- Batch queries for performance optimization

---

## Prerequisites

Before using this feature, ensure:

1. **Measurement Sheet** is created and contains measurement details
2. **Measurement Sheet Status** is set to "Approved"
3. **Measurement Sheet** is saved (document must be saved, not necessarily submitted)
4. **Customer** is linked to the Measurement Sheet
5. **Items** exist in the Item Master with valid item codes
6. **Item Rates** are configured (either in Item Price or Item standard_rate)

---

## User Guide

### Step 1: Create and Approve Measurement Sheet

1. Navigate to **Measurement Sheet** list
2. Create a new Measurement Sheet or open an existing one
3. Fill in all required fields:
   - Customer
   - Measurement Date
   - Measurement Method
   - Add Measurement Details with items (fabric, lining, etc.)
4. Save the Measurement Sheet
5. Change status to **"Approved"**
6. **Save the Measurement Sheet again** (status must be saved)

### Step 2: Create Sales Order from Measurement Sheet

1. Open the **approved and saved** Measurement Sheet
2. Look for the **"Create Sales Order"** button in the form toolbar (under "Create" menu)
3. Click the **"Create Sales Order"** button
4. The system will:
   - Validate the Measurement Sheet
   - Fetch Sales Order data (customer, items, rates)
   - Open a new Sales Order form with pre-populated data
   - **Note:** The Sales Order is NOT automatically saved - you can review and edit before saving
5. You will be automatically redirected to the new Sales Order form

### Step 3: Review and Edit Sales Order

1. Review the auto-populated items in the Sales Order form
2. Verify quantities and rates
3. Add any additional items if needed
4. Adjust delivery dates if required
5. **Save the Sales Order** (click Save button)
6. Submit for approval (if workflow is configured)

---

## Item Mapping Logic

The system maps items from Measurement Sheet's `measurement_details` to Sales Order's `items` table as follows:

### For Each Measurement Detail Row:

| Measurement Detail Field | Sales Order Item | Quantity | Rate |
|-------------------------|------------------|----------|------|
| `fabric_selected` | Item Code | `fabric_qty` | `fabric_rate` |
| `lining` | Item Code | `lining_qty` | `lining_rate` |
| `lead_rope` | Item Code | `lead_rope_qty` | `lead_rope_rate` |
| `track_rod` | Item Code | `track_rod_qty` | `track_rod_rate` |
| `selection` (Blinds) | Item Code | `1` | From Item Price or standard_rate |
| `stitching_pattern` | Item Code | `1` | `stitching_charge` |
| `fitting_type` | Item Code | `1` | `fitting_charge` |

### Rules:

- **Only items with valid values are added** (not empty/null)
- **Only items with quantity > 0 are added**
- **Each item becomes a separate row** in the Sales Order items table
- **Service charges (stitching, fitting) are added as separate item rows** with qty = 1
- **For Blinds selection**, the rate is fetched from Item Price (selling) or Item standard_rate
- **Items from multiple measurement detail rows** are all included in the Sales Order

---

## Status Workflow

### Button Visibility

The "Create Sales Order" button is only visible when:

1. Measurement Sheet status is **"Approved"**
2. Measurement Sheet is **saved** (has a name, not new)
3. Measurement Sheet has **no unsaved changes** (not dirty)

### Status Requirements

```
Draft → Customer Approval Pending → Approved
                                      ↓
                              Create Sales Order
```

**Status Descriptions:**
- **Draft**: Button not visible
- **Customer Approval Pending**: Button not visible
- **Approved**: Button visible (if saved and no unsaved changes)
- **Rejected**: Button not visible

---

## Integration Points

### 1. Measurement Sheet Integration
- Reads from Measurement Sheet doctype
- Validates status field
- Extracts data from measurement_details child table
- Links Sales Order back to Measurement Sheet

### 2. Sales Order Integration
- Creates new Sales Order document
- Populates custom field `measurement_sheet` (read-only)
- Maintains traceability to source Measurement Sheet

### 3. Item Master Integration
- Queries Item Price for selection items (Blinds)
- Falls back to Item.standard_rate
- Validates item codes exist

### 4. Customer Integration
- Transfers customer from Measurement Sheet
- Maintains customer linkage

### 5. Project Integration
- Transfers project from Measurement Sheet (if exists)
- Maintains project linkage

---

## Testing Guide

This section provides comprehensive testing procedures to verify the Sales Order from Measurement Sheet feature works correctly.

### Test Setup

Before starting tests, ensure:

1. **Test Data Preparation:**
   - Create at least one Customer in the system
   - Create Items in Item Master with appropriate Item Groups:
     - Fabric items (Item Group: "Main Fabric" or "Sheer Fabric")
     - Lining items (Item Group: "Lining")
     - Lead Rope items (Item Group: "Lead Rope Items")
     - Track/Rod items (Item Group: "Tracks", "Rods", or "Tracks & Rods")
     - Blinds items (Item Group: "Blinds Items")
     - Stitching items (Item Group: "Stitching")
     - Fitting items (Item Group: "Fitting")
   - Set Item Prices or standard_rate for items (especially for Blinds selection items)
   - Create Area master records (optional)
   - Create Pattern master records (optional, for Window Curtains/Roman Blinds)

2. **User Permissions:**
   - User must have read permission on Measurement Sheet
   - User must have create permission on Sales Order
   - User must have read permission on Item Master

3. **Browser Setup:**
   - Clear browser cache
   - Open browser console (F12) to monitor for errors
   - Ensure JavaScript is enabled

---

### Test Case 1: Basic Sales Order Creation

**Objective:** Verify Sales Order can be created from an approved Measurement Sheet with basic items.

**Prerequisites:**
- Measurement Sheet with status "Approved" and saved
- Customer linked to Measurement Sheet
- At least one Measurement Detail row with items

**Test Steps:**

1. **Prepare Measurement Sheet:**
   - Navigate to Measurement Sheet list
   - Create a new Measurement Sheet
   - Fill in:
     - Customer: Select a test customer
     - Measurement Date: Today's date
     - Measurement Method: "Customer Provided"
     - Status: "Approved"
   - Add Measurement Detail row:
     - Product Type: "Window Curtains"
     - Area: Select an area
     - Width: 100
     - Height: 120
     - Panels: 2
     - Fabric Selected: Select a fabric item
     - Lining: Select a lining item
   - Save the Measurement Sheet
   - Verify status is "Approved" and document is saved

2. **Create Sales Order:**
   - Open the approved Measurement Sheet
   - Verify "Create Sales Order" button is visible under "Create" menu
   - Click "Create Sales Order" button
   - Wait for navigation to Sales Order form

3. **Verify Sales Order:**
   - Verify customer field is auto-populated with Measurement Sheet customer
   - Verify transaction_date is set to today's date
   - Verify measurement_sheet field contains the Measurement Sheet name
   - Verify items table contains:
     - Fabric item with correct qty and rate
     - Lining item with correct qty and rate
   - Count total items in Sales Order items table
   - Verify quantities match Measurement Sheet

4. **Save Sales Order:**
   - Click Save button
   - Verify Sales Order is saved successfully
   - Verify Measurement Sheet link is functional (click to verify it opens correct Measurement Sheet)

**Expected Results:**
- ✅ Button is visible when Measurement Sheet is approved and saved
- ✅ Sales Order form opens with pre-populated data
- ✅ Customer, items, quantities, and rates are correctly populated
- ✅ Measurement Sheet link is set and functional
- ✅ Sales Order can be saved successfully

---

### Test Case 2: Button Visibility Tests

**Objective:** Verify button visibility based on Measurement Sheet status and save state.

#### Test 2.1: Button Not Visible for Draft Status

**Steps:**
1. Create a new Measurement Sheet
2. Set status to "Draft"
3. Save the Measurement Sheet
4. Refresh the form
5. Check for "Create Sales Order" button

**Expected Result:** ❌ Button is NOT visible

---

#### Test 2.2: Button Not Visible for Unsaved Changes

**Steps:**
1. Open an approved and saved Measurement Sheet
2. Make any change (e.g., change measurement_date)
3. Do NOT save
4. Check for "Create Sales Order" button

**Expected Result:** ❌ Button is NOT visible (document shows "Not Saved")

---

#### Test 2.3: Button Not Visible for New Document

**Steps:**
1. Create a new Measurement Sheet
2. Set status to "Approved"
3. Do NOT save
4. Check for "Create Sales Order" button

**Expected Result:** ❌ Button is NOT visible (document is new)

---

#### Test 2.4: Button Visible for Approved and Saved

**Steps:**
1. Open a Measurement Sheet with status "Approved"
2. Ensure the document is saved (no "Not Saved" indicator)
3. Refresh the form
4. Check for "Create Sales Order" button under "Create" menu

**Expected Result:** ✅ Button IS visible

---

### Test Case 3: Item Mapping - Window Curtains

**Objective:** Verify all items from Window Curtains measurement detail are mapped correctly.

**Prerequisites:**
- Measurement Sheet with Window Curtains product type
- Measurement Detail with all items:
  - fabric_selected, fabric_qty, fabric_rate
  - lining, lining_qty, lining_rate
  - lead_rope, lead_rope_qty, lead_rope_rate
  - track_rod, track_rod_qty, track_rod_rate
  - stitching_pattern, stitching_charge
  - fitting_type, fitting_charge

**Test Steps:**

1. Create Measurement Sheet with Window Curtains:
   - Product Type: "Window Curtains"
   - Fill in all required fields
   - Add all items (fabric, lining, lead rope, track rod, stitching, fitting)
   - Set quantities and rates
   - Status: "Approved"
   - Save

2. Create Sales Order from Measurement Sheet

3. Verify Sales Order items:
   - Count total items (should be 6)
   - Verify fabric item exists with correct qty and rate
   - Verify lining item exists with correct qty and rate
   - Verify lead_rope item exists with correct qty and rate
   - Verify track_rod item exists with correct qty and rate
   - Verify stitching_pattern item exists with qty=1 and rate=stitching_charge
   - Verify fitting_type item exists with qty=1 and rate=fitting_charge

**Expected Results:**
- ✅ All 6 items are present in Sales Order
- ✅ Quantities and rates match Measurement Sheet values
- ✅ Service charges have qty = 1

---

### Test Case 4: Item Mapping - Roman Blinds

**Objective:** Verify items from Roman Blinds measurement detail are mapped correctly.

**Test Steps:**

1. Create Measurement Sheet with Roman Blinds:
   - Product Type: "Roman Blinds"
   - Add items: fabric, lining, stitching, fitting
   - Status: "Approved"
   - Save

2. Create Sales Order from Measurement Sheet

3. Verify Sales Order items:
   - Verify fabric item exists
   - Verify lining item exists
   - Verify stitching_pattern item exists
   - Verify fitting_type item exists
   - Verify lead_rope item is NOT present
   - Verify track_rod item is NOT present

**Expected Results:**
- ✅ Only fabric, lining, stitching, and fitting items are present
- ✅ Quantities and rates are correct
- ✅ Lead rope and track rod items are excluded

---

### Test Case 5: Item Mapping - Blinds

**Objective:** Verify Blinds selection item is mapped correctly with rate fetching.

**Prerequisites:**
- Blinds selection item has Item Price configured OR standard_rate set

**Test Steps:**

1. Create Measurement Sheet with Blinds:
   - Product Type: "Blinds"
   - Add selection item
   - Add fitting item
   - Status: "Approved"
   - Save

2. Create Sales Order from Measurement Sheet

3. Verify Sales Order items:
   - Verify selection item exists with qty=1
   - Verify selection item rate matches Item Price (if exists) or standard_rate
   - Verify fitting_type item exists

**Expected Results:**
- ✅ Selection and fitting items are present
- ✅ Selection rate is correctly fetched from Item Price or standard_rate

---

### Test Case 6: Item Mapping - Tracks/Rods

**Objective:** Verify Tracks/Rods items are mapped correctly.

**Test Steps:**

1. Create Measurement Sheet with Tracks/Rods:
   - Product Type: "Tracks/Rods"
   - Add track_rod item
   - Add fitting item
   - Status: "Approved"
   - Save

2. Create Sales Order from Measurement Sheet

3. Verify Sales Order items:
   - Verify track_rod item exists
   - Verify fitting_type item exists
   - Verify fabric, lining, lead_rope items are NOT present

**Expected Results:**
- ✅ Only track_rod and fitting items are present
- ✅ Other product type items are excluded

---

### Test Case 7: Multiple Measurement Details

**Objective:** Verify Sales Order includes items from all measurement detail rows.

**Test Steps:**

1. Create Measurement Sheet with multiple rows:
   - Row 1: Window Curtains with fabric, lining
   - Row 2: Roman Blinds with fabric, lining
   - Row 3: Blinds with selection
   - Status: "Approved"
   - Save

2. Create Sales Order from Measurement Sheet

3. Verify Sales Order items:
   - Count total items (should be sum of all items from all rows)
   - Verify items from Row 1 are present
   - Verify items from Row 2 are present
   - Verify items from Row 3 are present
   - Verify quantities are correct for each item

**Expected Results:**
- ✅ All items from all Measurement Detail rows are included
- ✅ Items are not duplicated
- ✅ Quantities are correct

---

### Test Case 8: Items with Zero Quantity

**Objective:** Verify items with zero quantity are not added to Sales Order.

**Test Steps:**

1. Create Measurement Sheet:
   - Add Measurement Detail with:
     - fabric_selected with fabric_qty = 0
     - lining with lining_qty > 0
   - Status: "Approved"
   - Save

2. Create Sales Order from Measurement Sheet

3. Verify Sales Order items:
   - Verify fabric item is NOT present
   - Verify lining item IS present

**Expected Results:**
- ✅ Only items with quantity > 0 are added
- ✅ Items with qty = 0 are excluded

---

### Test Case 9: Missing/Empty Items

**Objective:** Verify items with empty/null values are not added.

**Test Steps:**

1. Create Measurement Sheet:
   - Add Measurement Detail with:
     - fabric_selected (has value)
     - lining (empty/null)
   - Status: "Approved"
   - Save

2. Create Sales Order from Measurement Sheet

3. Verify Sales Order items:
   - Verify fabric item IS present
   - Verify lining item is NOT present

**Expected Results:**
- ✅ Only items with valid values are added
- ✅ Empty/null items are excluded

---

### Test Case 10: Error Handling - Non-Approved Status

**Objective:** Verify error when trying to create Sales Order from non-approved Measurement Sheet.

**Test Steps:**

1. Create Measurement Sheet with status "Draft"
2. Save the Measurement Sheet
3. Try to call server method directly (via browser console):
   ```javascript
   frappe.call({
       method: "fabric_sense.fabric_sense.doctype.measurement_sheet.measurement_sheet.get_sales_order_data_from_measurement_sheet",
       args: { measurement_sheet_name: "MS-2025-0001" },
       callback: function(r) { console.log(r); }
   });
   ```

**Expected Results:**
- ❌ Error message: "Measurement Sheet 'MS-2025-0001' must be 'Approved' to create Sales Order. Current status: Draft"

---

### Test Case 11: Error Handling - Missing Customer

**Objective:** Verify error when Measurement Sheet has no customer.

**Test Steps:**

1. Create Measurement Sheet without customer (if possible)
2. Set status to "Approved"
3. Save
4. Try to create Sales Order

**Expected Results:**
- ❌ Error message: "Customer is required in Measurement Sheet to create Sales Order"

---

### Test Case 12: Error Handling - No Measurement Details

**Objective:** Verify error when Measurement Sheet has no measurement details.

**Test Steps:**

1. Create Measurement Sheet without measurement_details
2. Set status to "Approved"
3. Save
4. Try to create Sales Order

**Expected Results:**
- ❌ Error message: "Measurement Sheet must have at least one Measurement Detail to create Sales Order"

---

### Test Case 13: Error Handling - No Valid Items

**Objective:** Verify error when Measurement Sheet has no valid items to add.

**Test Steps:**

1. Create Measurement Sheet:
   - Add Measurement Detail with all items having qty = 0 or empty
   - Status: "Approved"
   - Save
2. Try to create Sales Order

**Expected Results:**
- ❌ Error message: "No valid items found in Measurement Sheet to create Sales Order"

---

### Test Case 14: Project Transfer

**Objective:** Verify project is transferred from Measurement Sheet to Sales Order.

**Test Steps:**

1. Create Measurement Sheet with project field set
2. Set status to "Approved"
3. Save
4. Create Sales Order from Measurement Sheet
5. Verify Sales Order project field

**Expected Results:**
- ✅ Project is correctly transferred to Sales Order

---

### Test Case 15: Multiple Sales Orders from Same Measurement Sheet

**Objective:** Verify multiple Sales Orders can be created from the same Measurement Sheet.

**Test Steps:**

1. Create Measurement Sheet with status "Approved" and save
2. Create first Sales Order from Measurement Sheet
3. Save first Sales Order
4. Go back to Measurement Sheet
5. Create second Sales Order from the same Measurement Sheet
6. Save second Sales Order
7. Verify both Sales Orders

**Expected Results:**
- ✅ Multiple Sales Orders can be created from the same Measurement Sheet
- ✅ All Sales Orders link to the same Measurement Sheet
- ✅ All Sales Orders have correct data

---

### Test Case 16: Rate Fetching for Selection Item

**Objective:** Verify rate is correctly fetched for Blinds selection item.

**Prerequisites:**
- Blinds selection item has Item Price configured OR standard_rate set

**Test Steps:**

1. Create Measurement Sheet with Blinds:
   - Product Type: "Blinds"
   - Selection item with Item Price configured
   - Status: "Approved"
   - Save
2. Create Sales Order from Measurement Sheet
3. Verify selection item rate in Sales Order
4. Compare with Item Price or standard_rate

**Expected Results:**
- ✅ Rate is correctly fetched from Item Price (if exists) or standard_rate
- ✅ Rate matches the source

---

### Test Case 17: Service Charges as Items

**Objective:** Verify stitching and fitting charges are added as separate item rows.

**Test Steps:**

1. Create Measurement Sheet:
   - Add Measurement Detail with:
     - stitching_pattern with stitching_charge > 0
     - fitting_type with fitting_charge > 0
   - Status: "Approved"
   - Save
2. Create Sales Order from Measurement Sheet
3. Verify Sales Order items:
   - Verify stitching_pattern item exists with qty=1 and rate=stitching_charge
   - Verify fitting_type item exists with qty=1 and rate=fitting_charge

**Expected Results:**
- ✅ Service charges are added as separate item rows
- ✅ Both have qty = 1
- ✅ Rates match charges from Measurement Sheet

---

### Test Case 18: Permission Testing

**Objective:** Verify permission checks work correctly.

**Test Steps:**

1. Login as user without read permission on Measurement Sheet
2. Try to create Sales Order from Measurement Sheet
3. Verify error message

**Expected Results:**
- ❌ Error: "Insufficient permissions to access Measurement Sheet"
- ❌ Error is logged in Error Log

---

### Test Case 19: Browser Console Testing

**Objective:** Verify no JavaScript errors occur during Sales Order creation.

**Test Steps:**

1. Open browser console (F12)
2. Clear console
3. Create Sales Order from Measurement Sheet
4. Check console for errors

**Expected Results:**
- ✅ No JavaScript errors in console
- ✅ No warnings related to the feature

---

### Test Case 20: Performance Testing

**Objective:** Verify performance with large number of items.

**Test Steps:**

1. Create Measurement Sheet with 10+ Measurement Detail rows
2. Each row with multiple items (fabric, lining, etc.)
3. Status: "Approved"
4. Save
5. Measure time to create Sales Order
6. Verify all items are included

**Expected Results:**
- ✅ Sales Order creation completes within reasonable time (< 5 seconds)
- ✅ All items are included correctly
- ✅ No performance degradation

---

## Test Checklist

Use this checklist to ensure all tests are completed:

- [ ] Test Case 1: Basic Sales Order Creation
- [ ] Test Case 2: Button Visibility Tests (all 4 sub-tests)
- [ ] Test Case 3: Item Mapping - Window Curtains
- [ ] Test Case 4: Item Mapping - Roman Blinds
- [ ] Test Case 5: Item Mapping - Blinds
- [ ] Test Case 6: Item Mapping - Tracks/Rods
- [ ] Test Case 7: Multiple Measurement Details
- [ ] Test Case 8: Items with Zero Quantity
- [ ] Test Case 9: Missing/Empty Items
- [ ] Test Case 10: Error Handling - Non-Approved Status
- [ ] Test Case 11: Error Handling - Missing Customer
- [ ] Test Case 12: Error Handling - No Measurement Details
- [ ] Test Case 13: Error Handling - No Valid Items
- [ ] Test Case 14: Project Transfer
- [ ] Test Case 15: Multiple Sales Orders from Same Measurement Sheet
- [ ] Test Case 16: Rate Fetching for Selection Item
- [ ] Test Case 17: Service Charges as Items
- [ ] Test Case 18: Permission Testing
- [ ] Test Case 19: Browser Console Testing
- [ ] Test Case 20: Performance Testing

---

## Testing Best Practices

1. **Test in Clean Environment:** Use test data, not production data
2. **Test All Product Types:** Ensure all 4 product types are tested
3. **Test Edge Cases:** Include zero quantities, empty fields, missing data
4. **Test Error Scenarios:** Verify all error messages are user-friendly
5. **Test Permissions:** Verify permission checks work correctly
6. **Monitor Console:** Check browser console for errors during testing
7. **Verify Data Integrity:** Ensure all data is correctly transferred
8. **Test Performance:** Verify feature works with large datasets
9. **Document Issues:** Record any bugs or issues found during testing
10. **Retest After Fixes:** Re-run tests after any code changes

---

## Troubleshooting

### Issue: "Create Sales Order" button not visible

**Possible Causes:**
- Measurement Sheet status is not "Approved"
- Measurement Sheet is not saved (has unsaved changes)
- Measurement Sheet is new (not yet saved)
- User doesn't have permission
- Helper JavaScript file not loaded

**Solution:**
- Ensure Measurement Sheet status is "Approved"
- Save the Measurement Sheet (click Save button)
- Ensure document is not new (has a name)
- Check user permissions
- Clear browser cache and reload
- Check browser console for JavaScript errors

---

### Issue: Error "Measurement Sheet must be 'Approved'"

**Possible Causes:**
- Measurement Sheet status is not "Approved"

**Solution:**
- Change Measurement Sheet status to "Approved"
- Save the Measurement Sheet

---

### Issue: Error "No valid items found"

**Possible Causes:**
- All items have quantity = 0
- All item fields are empty/null

**Solution:**
- Ensure at least one item has quantity > 0
- Fill in item fields in Measurement Details

---

### Issue: Items missing in Sales Order

**Possible Causes:**
- Item quantity is 0
- Item field is empty/null
- Item code doesn't exist in Item Master

**Solution:**
- Check Measurement Details for items with qty > 0
- Ensure all item fields are filled
- Verify items exist in Item Master

---

### Issue: Rates are zero

**Possible Causes:**
- Rates not set in Measurement Sheet
- Item doesn't have standard_rate or Item Price

**Solution:**
- Set rates in Measurement Sheet
- Configure Item Price or standard_rate for items

---

## Best Practices

1. **Always approve and save Measurement Sheet** before creating Sales Order
2. **Review Measurement Sheet** to ensure all items and quantities are correct
3. **Verify item rates** are set correctly in Measurement Sheet
4. **Review pre-populated Sales Order** before saving to ensure accuracy
5. **Check Sales Order items** after creation to ensure all items are included
6. **Add any additional items** if needed before saving the Sales Order
7. **Use Measurement Sheet link** in Sales Order to trace back to source
8. **Save the Sales Order manually** after reviewing the pre-populated data

---

## Related Documentation

- [Measurement Sheet Documentation](./MEASUREMENT_SHEET_README.md)
- [Sales Order from Measurement Sheet - Technical Implementation](./sales_order_from_measurement_sheet_technical.md)
- [Sales Order Creation Guidelines](./datailed_sections/sales_order_creation.md)
- [Measurement Sheet Creation Guide](./datailed_sections/measurement_sheet_creation.md)

---

## Version History

- **v1.1** (January 2025): Refactored implementation
  - Changed from auto-save to pre-population approach
  - Extracted button logic to helper file
  - Added permission checks and error logging
  - Fixed N+1 query problem with batch queries
  - Improved code organization with helper functions
  - Added constants for maintainability
  - Enhanced error messages with context

- **v1.0** (January 2025): Initial implementation
  - Auto-populate Sales Order from Measurement Sheet
  - Support for all product types
  - Service charges as separate items
  - Error handling and validation

---

**Document Version**: 1.1  
**Last Updated**: January 2025  
**Author**: Fabric Sense Development Team
