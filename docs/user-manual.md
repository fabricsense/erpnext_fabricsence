# Fabric Sense - User Manual

## Welcome to Fabric Sense

This manual provides step-by-step instructions for using the Fabric Sense ERP system. Whether you're a Salesperson or Manager, this guide will help you navigate the system efficiently.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Salesperson Guide](#salesperson-guide)
3. [Manager Guide](#manager-guide)
4. [Case I: Raw Fabric Sales](#case-i-raw-fabric-sales)
5. [Case II: Stitched Curtains](#case-ii-stitched-curtains)
6. [Common Tasks](#common-tasks)
7. [Reports and Analytics](#reports-and-analytics)
8. [Troubleshooting](#troubleshooting)
9. [FAQs](#faqs)

---

## Getting Started

### Logging In

1. Open your web browser
2. Navigate to your Fabric Sense URL (e.g., `https://yourcompany.erpnext.com`)
3. Enter your username and password
4. Click **Login**

### Dashboard Overview

After logging in, you'll see your dashboard with:
- **Quick Access Icons**: Shortcuts to frequently used modules
- **Recent Documents**: Your recently viewed or created documents
- **Notifications**: Pending approvals and alerts
- **To-Do List**: Your assigned tasks

### Navigation

**Main Menu** (Left Sidebar):
- **Home**: Dashboard
- **CRM**: Leads and Customers
- **Selling**: Sales Orders, Quotations
- **Stock**: Material Requests, Delivery Notes
- **Buying**: Purchase Orders
- **Accounts**: Invoices, Payments
- **Fabric Sense**: Custom modules (Measurement Sheet, Tailoring)

**Search Bar** (Top):
- Type to search for documents, customers, or items
- Use keyboard shortcut: `Ctrl + K` (Windows) or `Cmd + K` (Mac)

---

## Salesperson Guide

### Your Responsibilities

As a Salesperson, you will:
- ✅ Create and manage customer leads
- ✅ Record measurements
- ✅ Create sales orders
- ✅ Generate material requests
- ✅ Create invoices and delivery notes
- ✅ Process payments (pending manager approval)
- ✅ Communicate with customers

### Daily Workflow

1. **Morning**: Check pending leads and follow-ups
2. **Throughout Day**: Handle customer inquiries and create orders
3. **Evening**: Review pending approvals and update order status

---

## Manager Guide

### Your Responsibilities

As a Manager, you will:
- ✅ Approve sales orders
- ✅ Approve additional material requests
- ✅ Approve payments and discounts
- ✅ Monitor team performance
- ✅ Review financial reports

### Daily Workflow

1. **Morning**: Review pending approvals
2. **Throughout Day**: Approve/reject requests as they come
3. **Evening**: Review daily sales and financial reports

---

## Case I: Raw Fabric Sales

### Step 1: Create a Lead

**When**: Customer walks in or contacts via phone/WhatsApp

**How**:
1. Go to: **CRM > Lead > New**
2. Fill in the details:
   - **Lead Name**: Customer's name
   - **Email**: Customer's email address
   - **Mobile No**: Customer's phone number
   - **Inquiry Source**: Select (Walk-in/WhatsApp/Phone/Email)
   - **Fabric Requirements**: Describe what customer needs
3. Click **Save**

**Example**:
```
Lead Name: John Doe
Email: john@example.com
Mobile: +91 9876543210
Inquiry Source: Walk-in
Fabric Requirements: Living room curtains, 84x84 inches, 4 windows
```

---

### Step 2: Convert Lead to Customer

**When**: Customer decides to proceed with purchase

**How**:
1. Open the Lead document
2. Click **Customer** button in the toolbar
3. System creates Customer automatically
4. Verify customer information
5. Click **Save**

**Tip**: The customer record will have all information from the lead pre-filled.

---

### Step 3: Create Measurement Sheet

**When**: You need to record customer's requirements

**How**:

#### 3.1 Create New Measurement Sheet
1. Go to: **Fabric Sense > Estimation > New**
2. Select **Customer**
3. Set **Measurement Date** (defaults to today)
4. Select **Measurement Type**: Direct

#### 3.2 Add Items

Click **Add Row** in the Items table for each product.

#### For Window Curtains:

1. **Area**: Enter room name (e.g., "Living Room")
2. **Product Type**: Select "Window Curtain"
3. **Layer**: Select "Front" or "Back"
4. **Pattern**: Select pattern (e.g., "French Pleated")
5. **Width**: Enter width in inches (e.g., 84)
6. **Height**: Enter height in inches (e.g., 84)
7. **Panels**: Enter number of panels (e.g., 4)
8. **Adjust**: Enter adjustment if needed (default: 0)
9. **Fabric Type**: Select fabric from dropdown
10. **Lead Rope**: Select lead rope (optional)
11. **Lining**: Select lining (optional)
12. **Track/Rod Type**: Select track/rod (optional)

**System automatically calculates**:
- Quantity (in meters)
- Amount

#### For Roman Blinds:

1. **Area**: Enter room name
2. **Product Type**: Select "Roman Blind"
3. **Layer**: Select "Front" or "Back"
4. **Pattern**: Select pattern
5. **Width**: Enter width in inches
6. **Height**: Enter height in inches
7. **Panels**: Enter number of panels
8. **Adjust**: Enter adjustment if needed
9. **Fabric Type**: Select fabric
10. **Lining**: Select lining (optional)

**System automatically calculates**:
- Quantity (in meters)
- Square Feet
- Amount

#### For Blinds:

1. **Area**: Enter room name
2. **Product Type**: Select "Blind"
3. **Layer**: Select "Front" or "Back"
4. **Width**: Enter width in inches
5. **Height**: Enter height in inches
6. **Selection**: Enter material/color

**System automatically calculates**:
- Square Feet
- Amount

#### For Tracks/Rods:

1. **Area**: Enter room name
2. **Product Type**: Select "Track/Rod"
3. **Design**: Enter design type
4. **Width**: Enter width in inches
5. **Track/Rod Type**: Select from dropdown

**System automatically calculates**:
- Amount

#### 3.3 Add Multiple Products

You can add multiple rows for:
- Same area with different products (e.g., curtain + rod)
- Different areas (e.g., Living Room, Bedroom)

#### 3.4 Add Special Instructions

In the **Memo** field, add any special notes:
- Customer preferences
- Installation instructions
- Delivery requirements

#### 3.5 Save and Send for Approval

1. Click **Save**
2. Review the **Total Amount**
3. Click **Send for Approval** button

**What Happens Next**:
- Customer receives measurement sheet
- Customer reviews and approves/rejects
- You receive customer's decision

---

### Step 4: Create Sales Order

**When**: Customer approves the measurement sheet

**How**:
1. Open the approved Measurement Sheet
2. Click **Create Sales Order** button
3. System creates Sales Order with all items pre-populated
4. Review the order:
   - Customer details
   - Items and quantities
   - Delivery date
5. Add any additional items if needed
6. Click **Save**

**Important**: Do not submit yet! You need manager approval first.

---

### Step 5: Submit for Manager Approval

**How**:
1. Open the Sales Order
2. Click **Submit for Approval** button
3. System notifies manager
4. Wait for manager's decision

**Status Updates**:
- **Pending Manager Approval**: Waiting for manager
- **Approved**: Manager approved, proceed to next step
- **Rejected**: Manager rejected, revise and resubmit

**What to do if Rejected**:
1. Read rejection reason
2. Make necessary changes
3. Click **Submit for Approval** again

---

### Step 6: Check Stock and Create Material Request

**When**: Sales Order is approved

**How**:
1. Open the approved Sales Order
2. Click **Check Stock & Create Material Request** button
3. System automatically:
   - Checks stock availability
   - Creates Material Request (Issue) for in-stock items
   - Creates Material Request (Purchase) for out-of-stock items

**What Happens**:
- **In-Stock Items**: Reserved immediately
- **Out-of-Stock Items**: Purchase Order created automatically

---

### Step 7: Create Purchase Order (if needed)

**When**: Material Request (Purchase) is created

**How**:
1. Go to: **Buying > Material Request**
2. Open the Material Request
3. Click **Make > Purchase Order**
4. Select **Supplier**
5. Review items and quantities
6. Click **Save**
7. Click **Submit**

**What Happens Next**:
- System sends notification to vendor via WhatsApp/Email
- Vendor delivers items
- You receive notification when stock arrives

---

### Step 8: Create Purchase Receipt

**When**: Vendor delivers items

**How**:
1. Go to: **Stock > Purchase Order**
2. Open the Purchase Order
3. Click **Make > Purchase Receipt**
4. Verify items received
5. Enter **Accepted Quantity**
6. Click **Save**
7. Click **Submit**

**What Happens**:
- Stock is updated in the system
- You can now proceed with delivery

---

### Step 9: Create Sales Invoice

**When**: Order is ready for delivery

**How**:
1. Go to: **Selling > Sales Order**
2. Open the Sales Order
3. Click **Make > Sales Invoice**
4. Review invoice details
5. Click **Save**
6. Click **Submit**

**What Happens**:
- System sends invoice to customer via WhatsApp/Email
- Customer receives payment details

---

### Step 10: Send Order Ready Notification

**When**: Order is packed and ready

**How**:
1. Open the Sales Order
2. Click **Send Order Ready Notification** button
3. System notifies customer

**Customer receives**:
- Order ready message
- Pickup/delivery instructions
- Contact information

---

### Step 11: Create Delivery Note

**When**: Delivering items to customer

**How**:
1. Go to: **Selling > Sales Order**
2. Open the Sales Order
3. Click **Make > Delivery Note**
4. Review items to be delivered
5. Click **Save**
6. Click **Submit**

**What Happens**:
- System sends delivery note to customer via WhatsApp/Email
- Stock is updated
- Order status changes to "Delivered"

---

### Step 12: Create Payment Entry

**When**: Receiving payment from customer

**How**:

#### Without Discount:
1. Go to: **Accounts > Sales Invoice**
2. Open the Sales Invoice
3. Click **Make > Payment Entry**
4. Verify:
   - **Payment Type**: Receive
   - **Party**: Customer name
   - **Paid Amount**: Invoice amount
5. Select **Mode of Payment** (Cash/Card/Bank Transfer)
6. Click **Save**
7. Click **Submit for Approval** button
8. Wait for manager approval

#### With Discount:
1. Follow steps 1-4 above
2. Check **Has Discount** checkbox
3. Enter **Discount Amount**
4. Enter **Discount Reason**
5. System adjusts **Paid Amount** automatically
6. Click **Save**
7. Click **Submit for Approval** button
8. Wait for manager to approve discount first
9. Then wait for manager to approve payment

**Important**: Payment will not post to accounts until manager approves!

---

### Step 13: Mark Order as Complete

**When**: Payment is received and approved

**How**:
- System automatically marks order as complete
- No action needed from you

**Order Status**: Completed ✓

---

## Case II: Stitched Curtains

### Step 1: Create Lead and Convert to Customer

Same as Case I (Steps 1-2)

---

### Step 2: Create Project

**When**: Converting lead to customer for stitched curtains

**How**:
1. After creating customer, create Project
2. Go to: **Projects > Project**
3. Create projct

**Project includes**:
- Customer information
- Project timeline
- Task list (Measurement, Tailoring, Delivery)

---

### Step 3: Create Measurement Sheet

**Option A: Customer Provides Measurements Directly**

Follow Case I Step 3 (same process)

**Option B: Tailor Site Visit**

**How**:
1. Go to: **Fabric Sense > Estimation > New**
2. Select **Customer**
3. Set **Measurement Type**: "Tailor Visit"
4. Select **Tailor Assigned** from dropdown
5. Enter **Visit/Delivery Charge**
6. Click **Save**

**What Happens**:
- System sends notification to tailor via WhatsApp
- Tailor visits customer site
- Tailor takes measurements
- Tailor returns and you record measurements

**After Tailor Returns**:
1. Open the Measurement Sheet
2. Add items with measurements (follow Case I Step 3.2)
3. Click **Save**
4. Click **Send for Approval**

---

### Step 4: Mark Measurement Task Complete

**When**: Customer approves measurement sheet

**How**:
1. Go to: **Projects > Project**
2. Open the customer's project
3. Find "Measurement" task
4. Click on task
5. Change **Status** to "Completed"
6. Click **Save**

---

### Step 5: Create Sales Order

Same as Case I Step 4

**Additional**: Sales Order is linked to Project automatically

---

### Step 6: Get Manager Approval

Same as Case I Step 5

---

### Step 7: Create Tailoring Sheet

**When**: Sales Order is approved

**How**:
1. Go to: **Fabric Sense > Tailoring Sheet > New**
2. Click **Get from Measurement Sheet** button
3. Select the Measurement Sheet
4. System copies all items automatically
5. Review each item

**Add Adjustments** (if needed):
1. For each item, you can add:
   - **Adjustment Quantity**: Extra fabric needed (in meters)
   - **Adjustment Reason**: Why adjustment is needed
2. System calculates **Final Quantity** = Original + Adjustment
3. Click **Save**

**Example Adjustment**:
```
Original Quantity: 15 meters
Adjustment Quantity: 2 meters
Adjustment Reason: "Extra fabric for pleating"
Final Quantity: 17 meters
```

---

### Step 8: Create Material Request

Same as Case I Step 6

**Note**: Material Request is created from Tailoring Sheet (not Measurement Sheet)

---

### Step 9: Create Purchase Order (if needed)

Same as Case I Step 7

---

### Step 10: Create Tailoring Job Card

**When**: All materials are ready

**How**:
1. Go to: **Fabric Sense > Tailoring Job Card > New**
2. Fill in details:
   - **Project**: Select customer's project
   - **Sales Order**: Select the sales order
   - **Tailoring Sheet**: Select the tailoring sheet
   - **Tailor**: Select tailor from dropdown
   - **Tailor Contact**: Enter phone number
   - **Start Date**: When tailoring should begin
   - **End Date**: Expected completion date
   - **Tailoring Charge**: Enter charge amount
   - **Travel Charge**: Enter if tailor visited site
3. Add items in the Items table
4. Click **Save**

**What Happens**:
- System sends notification to tailor via WhatsApp
- Tailor receives job details and timeline

---

### Step 11: Monitor Tailoring Progress

**Automatic Status Updates**:

**On Start Date**:
- System automatically changes status to "Started"
- Stock is consumed (materials issued)
- You receive notification

**On End Date**:
- System automatically changes status to "Completed"
- System calculates total cost
- You receive notification

**Manual Status Check**:
1. Go to: **Fabric Sense > Tailoring Job Card**
2. Open the job card
3. View current status

**Status Options**:
- **Not Started**: Before start date
- **Started**: Work in progress
- **Completed**: Work finished

---

### Step 12: Create Tailor Payment

**When**: Tailoring job is completed

**How**:
1. Open the Tailoring Job Card
2. Review **Total Cost** (Tailoring Charge + Travel Charge)
3. Click **Create Payment** button
4. System creates Payment Entry:
   - **Payment Type**: Pay
   - **Party**: Tailor
   - **Paid Amount**: Total cost
5. Select **Mode of Payment**
6. Click **Save**
7. Click **Submit**

**Payment Types**:
- **Per Job**: Pay for each job individually
- **Monthly**: Accumulate and pay monthly (track in system)

---

### Step 13: Create Sales Invoice

Same as Case I Step 9

**Note**: Invoice includes all costs (fabric + tailoring + accessories)

---

### Step 14: Send Order Ready Notification

Same as Case I Step 10

---

### Step 15: Create Delivery Note

Same as Case I Step 11

**Important**: Stock update only for items not consumed during tailoring (e.g., extra accessories)

---

### Step 16: Create Payment Entry

Same as Case I Step 12

---

## Common Tasks

### Adding Additional Items to Sales Order

**Scenario**: Customer requests more items after order is placed

**How**:
1. Open the Sales Order
2. Click **Add Row** in Items table
3. Add new items
4. Click **Save**
5. Create **Material Request** for new items
6. Mark as **Additional Request**
7. Enter **Reason**: "Customer Requested Additional Items"
8. Click **Submit for Approval**
9. Wait for manager approval

**Important**: Manager must approve additional material requests!

---

**Important**: 
- Do NOT update the Sales Order
- Do NOT create invoice for replacement
- Only update stock after manager approves

---

### Searching for Documents

**Quick Search**:
1. Press `Ctrl + K` (or `Cmd + K` on Mac)
2. Type document name or number
3. Select from results

**Advanced Search**:
1. Go to the document list (e.g., Sales Order)
2. Click **Filters** button
3. Add filters:
   - Customer name
   - Date range
   - Status
   - Amount range
4. Click **Apply**

---

### Printing Documents

**How**:
1. Open any document
2. Click **Print** button (top right)
3. Select **Print Format**
4. Click **Print**

**Available Formats**:
- Standard
- Detailed
- Compact

---

## Manager Guide - Approval Tasks

### Approving Sales Orders

**How**:
1. Go to: **Selling > Sales Order**
2. Filter by **Approval Status**: "Pending Manager Approval"
3. Open the Sales Order
4. Review:
   - Customer details
   - Items and quantities
   - Pricing
   - Total amount
5. Decision:

**To Approve**:
1. Click **Approve** button (under Manager Actions)
2. System submits the order
3. Customer receives approval notification

**To Reject**:
1. Click **Reject** button (under Manager Actions)
2. Enter **Rejection Reason**
3. Click **Submit**
4. Salesperson receives notification

---

### Approving Additional Material Requests

**How**:
1. Go to: **Stock > Material Request**
2. Filter by **Is Additional Request**: Yes
3. Filter by **Approval Status**: "Pending"
4. Open the Material Request
5. Review:
   - Reason for additional request
   - Items and quantities
   - Related Sales Order
6. Click **Approve Additional Request** button

**What to Check**:
- Is the reason valid?
- Are quantities reasonable?
- Is this the first additional request or multiple?

---

### Approving Payments

**Without Discount**:
1. Go to: **Accounts > Payment Entry**
2. Filter by **Payment Approval Status**: "Pending"
3. Open the Payment Entry
4. Review:
   - Customer/Party
   - Amount
   - Mode of payment
5. Click **Approve Payment** button (under Manager Actions)

**With Discount**:
1. Follow steps 1-4 above
2. Review **Discount Amount** and **Discount Reason**
3. First, click **Approve Discount** button
4. Then, click **Approve Payment** button

**Important**: Two-step approval for discounted payments!

**What to Check**:
- Is discount justified?
- Is discount within policy limits?
- Is payment amount correct after discount?

---

## FAQs

### General Questions

**Q: How do I change my password?**
A: Click on your profile picture (top right) > My Settings > Change Password

**Q: Can I work offline?**
A: No, Fabric Sense requires internet connection.

**Q: How do I get help?**
A: Click the Help icon (?) in the top menu or contact your system administrator.

---

### Sales Questions

**Q: Can I edit a submitted Sales Order?**
A: No, but you can cancel and amend it. Or add additional items through Material Request.

**Q: How long does manager approval take?**
A: Typically within a few hours. Manager receives instant notification.

**Q: Can I create multiple measurement sheets for one customer?**
A: Yes, each order can have its own measurement sheet.

---

## Quick Reference

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + K` | Quick search |
| `Ctrl + S` | Save document |
| `Ctrl + G` | Go to list |
| `Ctrl + N` | New document |
| `Esc` | Close dialog |

### Status Meanings

**Sales Order**:
- **Draft**: Being created
- **Pending Manager Approval**: Awaiting approval
- **Approved**: Manager approved
- **To Deliver**: Ready for delivery
- **Completed**: Fully delivered and paid

**Material Request**:
- **Draft**: Being created
- **Pending**: Awaiting manager approval (additional)
- **Submitted**: Approved and active
- **Issued**: Stock issued
- **Completed**: Fully processed

**Payment Entry**:
- **Pending**: Awaiting manager approval
- **Discount Approved**: Discount approved, payment pending
- **Payment Approved**: Fully approved and posted

**Tailoring Job Card**:
- **Not Started**: Before start date
- **Started**: Work in progress
- **Completed**: Work finished

---

## Contact Support

**For Technical Issues**:
- Email: support@yourcompany.com
- Phone: +91 XXXXXXXXXX

**For Business Questions**:
- Contact your Manager
- Email: manager@yourcompany.com

**System Administrator**:
- Email: admin@yourcompany.com

---

## Document Version

**Version**: 1.0  
**Last Updated**: December 2024  
**Next Review**: March 2025

---

**End of User Manual**

For more detailed technical information, refer to the Technical Implementation Guide.

For workflow diagrams, refer to the Workflow Diagrams document.

For business process details, refer to Case I and Case II Implementation Guides.
