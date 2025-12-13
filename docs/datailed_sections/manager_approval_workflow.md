# Manager Approval Status Workflow for Sales Order

## Overview
This document describes the Manager Approval Status workflow implemented for Sales Order doctype. The workflow ensures that all sales orders require manager approval before submission.

## Feature Description
The Manager Approval Status field is a custom field added to the Sales Order doctype that controls the approval workflow. It has three possible values:
- **Pending** (Default)
- **Approved**
- **Rejected**

---

## Implementation Details

### 1. Custom Field Configuration

**Field Name:** `manager_approval_status`  
**Field Type:** Select  
**Options:** Pending, Approved, Rejected  
**Default Value:** Pending  
**Location:** After "Order Type" field  
**Properties:**
- Read Only: Yes
- In List View: Yes
- In Standard Filter: Yes
- In Global Search: Yes

**File:** `fabric_sense/fabric_sense/custom/sales_order.json`

---

### 2. Client-Side Logic (JavaScript)

**File:** `fabric_sense/public/js/sales_order.js`

#### A. Approve/Reject Buttons (Sales Manager)
- **Displayed When:**
  - User has "Sales Manager" role
  - Manager Approval Status = "Pending"
  - Document is saved (not new)
  - Document status = Draft (docstatus = 0)

- **Approve Button:**
  - Shows confirmation dialog
  - Changes status to "Approved"
  - Shows success alert
  - Reloads document

- **Reject Button:**
  - Prompts for rejection reason (mandatory)
  - Changes status to "Rejected"
  - Adds comment with rejection reason
  - Shows rejection alert
  - Reloads document

#### B. Resubmit Button (Sales User)
- **Displayed When:**
  - User has "Sales User" role
  - Manager Approval Status = "Rejected"
  - Document is saved (not new)
  - Document status = Draft (docstatus = 0)

- **Functionality:**
  - Shows confirmation dialog
  - Changes status back to "Pending"
  - Shows resubmission alert
  - Reloads document

#### C. Submission Validation
- **Blocks submission when:**
  - Manager Approval Status = "Pending"
    - Message: "Manager approval is pending. Manager approval is needed to submit this sales order."
  - Manager Approval Status = "Rejected"
    - Message: "Manager rejected this record. Manager approval is needed to submit this sales order."

- **Allows submission when:**
  - Manager Approval Status = "Approved"

#### D. Hide Update Items Button
- **Condition:** Manager Approval Status = "Approved"
- **Action:** Clears inner toolbar to hide the "Update Items" button

---

## Workflow Process

### Process Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Sales Order Creation                          │
│                  (Status: Pending by default)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Sales Manager  │
                    │   Reviews      │
                    └────────┬───────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        ┌──────────────┐          ┌──────────────┐
        │   APPROVE    │          │    REJECT    │
        │              │          │  (+ Reason)  │
        └──────┬───────┘          └──────┬───────┘
               │                         │
               ▼                         ▼
        Status: Approved          Status: Rejected
               │                         │
               │                         ▼
               │                  ┌──────────────┐
               │                  │  Sales User  │
               │                  │  Resubmits   │
               │                  └──────┬───────┘
               │                         │
               │                         ▼
               │                  Status: Pending
               │                         │
               └─────────┬───────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Submit Document │
                │   (Allowed)     │
                └─────────────────┘
```

---

## Step-by-Step Process

### Step 1: Create Sales Order
1. Navigate to Sales Order list
2. Click "New" to create a new Sales Order
3. Fill in required fields (Customer, Items, etc.)
4. Save the document
5. **Manager Approval Status** automatically set to **"Pending"**

### Step 2: Manager Review (Sales Manager)
1. Sales Manager opens the saved Sales Order
2. Reviews the order details
3. Two buttons appear under "Manager Approval" group:
   - **Approve** (Green button)
   - **Reject** (Red button)

#### Option A: Approve
1. Click **"Approve"** button
2. Confirmation dialog appears: "Are you sure you want to approve this Sales Order?"
3. Click "Yes"
4. Status changes to **"Approved"**
5. Success alert: "Sales Order Approved Successfully"
6. Document reloads

#### Option B: Reject
1. Click **"Reject"** button
2. Dialog prompts for "Rejection Reason" (mandatory field)
3. Enter reason and click "Submit"
4. Status changes to **"Rejected"**
5. Comment added with rejection reason
6. Alert: "Sales Order Rejected"
7. Document reloads

### Step 3A: Submit Approved Order
1. If status is **"Approved"**, user can submit the Sales Order
2. Click "Submit" button
3. Document submits successfully
4. **Update Items** button is hidden (cannot modify approved orders)

### Step 3B: Resubmit Rejected Order (Sales User)
1. If status is **"Rejected"**, Sales User sees **"Resubmit for Manager Approval"** button
2. Click the button
3. Confirmation dialog: "Are you sure you want to resubmit this Sales Order for manager approval?"
4. Click "Yes"
5. Status changes back to **"Pending"**
6. Alert: "Sales Order resubmitted for approval"
7. Document reloads
8. Manager can review again (back to Step 2)

### Step 4: Blocked Submission Scenarios
1. **If status is "Pending":**
   - Click "Submit" button
   - Error message: "Manager approval is pending. Manager approval is needed to submit this sales order."
   - Submission blocked

2. **If status is "Rejected":**
   - Click "Submit" button
   - Error message: "Manager rejected this record. Manager approval is needed to submit this sales order."
   - Submission blocked

---

## Test Cases

### Test Case 1: Default Status on Creation
**Objective:** Verify that new Sales Orders default to "Pending" status

**Steps:**
1. Create a new Sales Order
2. Fill in required fields
3. Save the document

**Expected Result:**
- Manager Approval Status = "Pending"

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 2: Approve Button Visibility (Sales Manager)
**Objective:** Verify Approve/Reject buttons show for Sales Manager

**Pre-conditions:**
- User has "Sales Manager" role
- Sales Order is saved
- Manager Approval Status = "Pending"
- Document status = Draft

**Steps:**
1. Login as Sales Manager
2. Open a saved Sales Order with Pending status

**Expected Result:**
- "Approve" button visible (green)
- "Reject" button visible (red)
- Both buttons under "Manager Approval" group

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 3: Approve Functionality
**Objective:** Verify approval process works correctly

**Pre-conditions:**
- User has "Sales Manager" role
- Sales Order status = "Pending"

**Steps:**
1. Click "Approve" button
2. Click "Yes" in confirmation dialog

**Expected Result:**
- Manager Approval Status changes to "Approved"
- Success alert displayed: "Sales Order Approved Successfully"
- Document reloads
- Approve/Reject buttons disappear

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 4: Reject Functionality with Reason
**Objective:** Verify rejection process with mandatory reason

**Pre-conditions:**
- User has "Sales Manager" role
- Sales Order status = "Pending"

**Steps:**
1. Click "Reject" button
2. Enter rejection reason in the prompt
3. Click "Submit"

**Expected Result:**
- Manager Approval Status changes to "Rejected"
- Comment added with rejection reason
- Alert displayed: "Sales Order Rejected"
- Document reloads
- Approve/Reject buttons disappear

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 5: Reject Without Reason (Validation)
**Objective:** Verify rejection reason is mandatory

**Pre-conditions:**
- User has "Sales Manager" role
- Sales Order status = "Pending"

**Steps:**
1. Click "Reject" button
2. Leave rejection reason empty
3. Try to submit

**Expected Result:**
- Validation error: Field is required
- Status does not change
- Dialog remains open

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 6: Resubmit Button Visibility (Sales User)
**Objective:** Verify Resubmit button shows for Sales User

**Pre-conditions:**
- User has "Sales User" role
- Sales Order is saved
- Manager Approval Status = "Rejected"
- Document status = Draft

**Steps:**
1. Login as Sales User
2. Open a rejected Sales Order

**Expected Result:**
- "Resubmit for Manager Approval" button visible (blue)

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 7: Resubmit Functionality
**Objective:** Verify resubmission changes status back to Pending

**Pre-conditions:**
- User has "Sales User" role
- Sales Order status = "Rejected"

**Steps:**
1. Click "Resubmit for Manager Approval" button
2. Click "Yes" in confirmation dialog

**Expected Result:**
- Manager Approval Status changes to "Pending"
- Alert displayed: "Sales Order resubmitted for approval"
- Document reloads
- Resubmit button disappears

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 8: Block Submission - Pending Status
**Objective:** Verify submission is blocked when status is Pending

**Pre-conditions:**
- Sales Order status = "Pending"
- Document status = Draft

**Steps:**
1. Click "Submit" button

**Expected Result:**
- Submission blocked
- Error message: "Manager approval is pending. Manager approval is needed to submit this sales order."
- Document remains in Draft status

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 9: Block Submission - Rejected Status
**Objective:** Verify submission is blocked when status is Rejected

**Pre-conditions:**
- Sales Order status = "Rejected"
- Document status = Draft

**Steps:**
1. Click "Submit" button

**Expected Result:**
- Submission blocked
- Error message: "Manager rejected this record. Manager approval is needed to submit this sales order."
- Document remains in Draft status

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 10: Allow Submission - Approved Status
**Objective:** Verify submission is allowed when status is Approved

**Pre-conditions:**
- Sales Order status = "Approved"
- Document status = Draft
- All other required fields filled

**Steps:**
1. Click "Submit" button

**Expected Result:**
- Document submits successfully
- Document status changes to "Submitted"
- No error messages

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 11: Hide Update Items Button
**Objective:** Verify Update Items button is hidden when Approved

**Pre-conditions:**
- Sales Order status = "Approved"
- Document status = Draft

**Steps:**
1. Open the Sales Order
2. Check for "Update Items" button

**Expected Result:**
- "Update Items" button is not visible
- Inner toolbar is cleared

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 12: Buttons Not Visible for Non-Managers
**Objective:** Verify approval buttons don't show for users without Sales Manager role

**Pre-conditions:**
- User does NOT have "Sales Manager" role
- Sales Order status = "Pending"

**Steps:**
1. Login as regular user (not Sales Manager)
2. Open a pending Sales Order

**Expected Result:**
- Approve button NOT visible
- Reject button NOT visible

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 13: Resubmit Not Visible for Non-Sales Users
**Objective:** Verify Resubmit button doesn't show for users without Sales User role

**Pre-conditions:**
- User does NOT have "Sales User" role
- Sales Order status = "Rejected"

**Steps:**
1. Login as user without Sales User role
2. Open a rejected Sales Order

**Expected Result:**
- "Resubmit for Manager Approval" button NOT visible

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 14: Buttons Not Visible on New (Unsaved) Document
**Objective:** Verify buttons don't appear on unsaved documents

**Pre-conditions:**
- User has "Sales Manager" role

**Steps:**
1. Create a new Sales Order
2. Fill in fields but DO NOT save

**Expected Result:**
- Approve button NOT visible
- Reject button NOT visible
- Buttons only appear after saving

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 15: Buttons Not Visible on Submitted Documents
**Objective:** Verify buttons don't appear on submitted documents

**Pre-conditions:**
- Sales Order is submitted (docstatus = 1)

**Steps:**
1. Open a submitted Sales Order

**Expected Result:**
- Approve button NOT visible
- Reject button NOT visible
- Resubmit button NOT visible

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 16: Field is Read-Only
**Objective:** Verify Manager Approval Status field cannot be manually edited

**Steps:**
1. Open a Sales Order
2. Try to manually change Manager Approval Status field

**Expected Result:**
- Field is read-only
- Cannot be edited directly
- Can only be changed via buttons

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 17: Status Visible in List View
**Objective:** Verify Manager Approval Status is visible in list view

**Steps:**
1. Navigate to Sales Order list
2. Check column headers

**Expected Result:**
- "Manager Approval Status" column visible in list view
- Status values displayed for each record

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 18: Status Filterable
**Objective:** Verify users can filter by Manager Approval Status

**Steps:**
1. Navigate to Sales Order list
2. Add filter for "Manager Approval Status"
3. Select "Pending"

**Expected Result:**
- Filter applied successfully
- Only records with "Pending" status shown

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 19: Complete Workflow End-to-End
**Objective:** Test complete approval workflow from creation to submission

**Steps:**
1. Create new Sales Order (Status: Pending)
2. Save document
3. Login as Sales Manager
4. Reject with reason "Price too high"
5. Login as Sales User
6. Resubmit for approval (Status: Pending)
7. Login as Sales Manager
8. Approve (Status: Approved)
9. Submit document

**Expected Result:**
- All status transitions work correctly
- Rejection reason saved in comments
- Document submits successfully
- No errors throughout workflow

**Status:** ✅ Pass / ❌ Fail

---

### Test Case 20: Console Logging (Debug)
**Objective:** Verify debug console logs are working

**Steps:**
1. Open browser console (F12)
2. Open a Sales Order

**Expected Result:**
- Console logs display:
  - Manager Approval Status
  - User Roles
  - Is Sales Manager
  - Is Sales User
  - Is Local
  - Doc Status

**Status:** ✅ Pass / ❌ Fail

---

## User Roles and Permissions

### Sales Manager Role
**Permissions:**
- View all Sales Orders
- Approve Sales Orders (Pending → Approved)
- Reject Sales Orders (Pending → Rejected)
- Cannot resubmit rejected orders

### Sales User Role
**Permissions:**
- Create Sales Orders
- View assigned Sales Orders
- Resubmit rejected orders (Rejected → Pending)
- Cannot approve/reject orders

### Other Roles
**Permissions:**
- View Sales Orders (based on standard permissions)
- Cannot approve, reject, or resubmit

---

## Technical Notes

### Files Modified
1. `fabric_sense/fabric_sense/custom/sales_order.json`
   - Added custom field definition

2. `fabric_sense/public/js/sales_order.js`
   - Added button logic
   - Added submission validation
   - Added debug logging

### Dependencies
- Frappe Framework
- ERPNext
- Sales Order doctype

### Browser Compatibility
- Chrome/Chromium (Recommended)
- Firefox
- Safari
- Edge

---

## Troubleshooting

### Issue 1: Buttons Not Showing
**Possible Causes:**
- User doesn't have required role
- Document not saved
- Document already submitted
- Cache not cleared

**Solution:**
1. Verify user has "Sales Manager" or "Sales User" role
2. Save the document first
3. Clear browser cache (Ctrl+Shift+R)
4. Check console logs for debugging

### Issue 2: Status Not Changing
**Possible Causes:**
- Field is read-only in database
- Permission issues
- JavaScript errors

**Solution:**
1. Check browser console for errors
2. Verify field permissions in Customize Form
3. Clear cache and reload

### Issue 3: Submission Not Blocked
**Possible Causes:**
- JavaScript not loaded
- Validation logic bypassed
- Cache issue

**Solution:**
1. Clear browser cache
2. Check if `before_submit` event is firing
3. Verify `frappe.validated = false` is being set

---

## Future Enhancements

### Potential Improvements
1. **Email Notifications:**
   - Notify Sales Manager when order needs approval
   - Notify Sales User when order is approved/rejected

2. **Approval History:**
   - Track all approval/rejection actions
   - Show approval timeline

3. **Multi-level Approval:**
   - Add Senior Manager approval for high-value orders
   - Conditional approval based on order amount

4. **Bulk Approval:**
   - Allow managers to approve multiple orders at once

5. **Approval Dashboard:**
   - Show pending approvals count
   - Quick approve/reject from dashboard

6. **Auto-approval Rules:**
   - Auto-approve orders below certain threshold
   - Auto-approve for trusted customers

---

## Changelog

### Version 1.0.0 (2025-12-10)
- Initial implementation
- Added Manager Approval Status field
- Added Approve/Reject buttons for Sales Manager
- Added Resubmit button for Sales User
- Added submission validation
- Added Hide Update Items functionality
- Added confirmation dialogs
- Added rejection reason prompt
- Added visual styling for buttons

---

## Support and Contact

For issues or questions regarding this feature, please contact:
- **Development Team:** innogenio
- **Email:** dona@gmail.com

---

## References

- [Frappe Framework Documentation](https://frappeframework.com/docs)
- [ERPNext Documentation](https://docs.erpnext.com/)
- [Sales Order Doctype](https://docs.erpnext.com/docs/user/manual/en/selling/sales-order)

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-10  
**Author:** Development Team  
**Status:** Active
