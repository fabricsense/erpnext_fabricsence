# Case II: Stitched Curtains - Implementation Guide

## Overview

This guide provides detailed implementation instructions for the **Stitched Curtains** workflow, where customers order custom-made curtains with professional tailoring services.

---

## Key Differences from Case I

1. **Project Management**: Each customer order creates a Project
2. **Tailoring Sheet**: Additional DocType for tailoring-specific measurements with adjustments
3. **Tailor Assignment**: Job card system for assigning and tracking tailoring work
4. **Material Consumption**: Stock updates at tailoring start (not delivery)
5. **Tailor Payments**: Track and manage tailor compensation
6. **Site Visits**: Optional tailor visits for measurements with travel charges

---

## Implementation Sections

### 1. Lead to Customer + Project Creation
- Simultaneous customer and project creation
- Project linking to customer orders

### 2. Measurement Process
- **Option A**: Customer provides measurements directly
- **Option B**: Tailor site visit for measurements
- Measurement sheet with delivery/visit charges
- Tailor notification for site visits

### 3. Sales Order with Manager Approval
- Convert measurement sheet to sales order
- Manager approval workflow
- Customer notification on approval

### 4. Tailoring Sheet Management
- Copy measurement sheet to tailoring sheet
- Adjustment section for corrections
- Link to sales order and project

### 5. Material Request & Procurement
- Material request from tailoring sheet
- Issue/Purchase types
- Manager approval for multiple requests
- Purchase order and vendor notifications

### 6. Tailor Assignment & Job Card
- Create tailoring job card
- Assign tailor with details:
  - Tailor name
  - Tailoring charge
  - Travel charge (if applicable)
  - Start and end dates
- Tailor notification (WhatsApp)

### 7. Tailoring Execution
- Job status tracking (Started/Ended)
- Stock update at job start (material consumption)
- Automatic status updates based on dates

### 8. Tailoring Completion
- Cost calculation (tailoring + travel charges)
- Tailor payment tracking
- Mark job as complete

### 9. Invoicing & Delivery
- Sales invoice creation
- Customer notification
- Order ready notification
- Delivery note generation

### 10. Payment Processing
- Payment entry with discount options
- Manager approval workflow
- Account posting

---

## Key Custom DocTypes

### 1. Tailoring Sheet
**Purpose**: Copy of measurement sheet with adjustment capabilities

**Main Fields**:
- Customer
- Project
- Sales Order
- Measurement Sheet (reference)
- Total Amount
- Status

**Child Table: Tailoring Sheet Item**
- All fields from Measurement Sheet Item
- Additional: `adjustment_quantity` field
- Additional: `adjustment_reason` field
- Calculated: `final_quantity` (original + adjustment)

### 2. Tailoring Job Card
**Purpose**: Track tailoring assignments and costs

**Main Fields**:
- Project
- Sales Order
- Tailoring Sheet
- Tailor (Link to Supplier/Employee)
- Tailor Contact
- Start Date
- End Date
- Expected Completion Date
- Actual Completion Date
- Status (Not Started/Started/Completed)
- Tailoring Charge
- Travel Charge
- Total Cost (calculated)
- Payment Status (Pending/Paid)
- Payment Reference

**Child Table: Job Card Items**
- Item Code
- Quantity
- Description

### 3. Project Task Enhancement
**Custom Fields for Project Tasks**:
- Task Type (Measurement/Tailoring/Delivery)
- Assigned Tailor
- Measurement Date
- Tailoring Start Date
- Tailoring End Date

---

## Workflow Diagrams

### Complete Case II Flow

```
Customer Inquiry → Lead
    ↓
Lead → Customer + Project
    ↓
Measurement (Direct OR Tailor Visit)
    ↓
[If Tailor Visit] → Notify Tailor → Site Visit → Record Measurements
    ↓
Measurement Sheet → Customer Approval
    ↓
Sales Order → Manager Approval → Customer Notification
    ↓
Tailoring Sheet (with Adjustments)
    ↓
Material Request (Issue/Purchase)
    ↓
[If Purchase] → Purchase Order → Vendor Notification → Purchase Receipt
    ↓
Tailor Assignment → Job Card → Tailor Notification
    ↓
Tailoring Start → Stock Update (Material Consumption)
    ↓
Tailoring Complete → Cost Calculation
    ↓
Tailor Payment Processing
    ↓
Sales Invoice → Customer Notification
    ↓
Order Ready Notification
    ↓
Delivery Note → Customer Notification
    ↓
Payment Entry → Manager Approval → Account Posting
```

---

## Key Business Rules

### 1. Measurement Options
- **Direct**: Customer provides measurements → Create measurement sheet immediately
- **Tailor Visit**: Assign tailor → Notify tailor → Tailor visits → Record measurements

### 2. Adjustment Handling
- Tailoring sheet allows adjustments to original measurements
- Adjustments tracked with reasons
- Final quantity = Original quantity + Adjustment quantity

### 3. Stock Management
- Materials consumed at tailoring START (not delivery)
- Stock entry created automatically when job status changes to "Started"
- Delivery note updates stock only for non-tailored items (accessories, etc.)

### 4. Cost Calculation
- Tailoring cost = Base tailoring charge + Travel charge (if applicable)
- Automatically calculated when job completes
- Travel charge applies only if tailor visited customer site

### 5. Approval Requirements
- Sales Order: Manager approval required
- Multiple Material Requests: Manager approval required
- Payment: Manager approval required (+ discount approval if applicable)

---

## Special Considerations

### 1. Tailor Management
- Tailors can be managed as Suppliers or Employees
- Store tailor contact information for notifications
- Track tailor performance and payment history

### 2. Site Visit Charges
- Add delivery/visit charge as line item in measurement sheet
- Include in sales order total
- Track in job card for cost analysis

### 3. Project Tracking
- All documents linked to project
- Project dashboard shows:
  - Measurement status
  - Tailoring progress
  - Payment status
  - Delivery status
---

See `technical-implementation.md` for detailed code and configuration.
