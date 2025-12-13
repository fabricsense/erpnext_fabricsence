# Measurement Sheet Creation - Implementation Guide

## Overview
The Measurement Sheet is a critical doctype in the Fabric Sense application that captures all necessary measurements and pricing details for customer orders. It serves as the foundation for creating Sales Orders and managing the entire order fulfillment process.

## Doctype: Measurement Sheet

### Purpose
- Collect measurements for customer-required materials or stitched items
- Calculate fabric quantities and pricing automatically
- Support multiple product types (Window Curtains, Roman Blinds, Blinds, Tracks/Rods)
- Enable approval workflow before Sales Order creation
- Track measurement collection method (customer-provided vs tailor-assigned)

---

## Field Structure

### Basic Information Fields

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `naming_series` | Data | Auto-naming series (e.g., MS-.YYYY.-.####) | Yes |
| `customer` | Link (Customer) | Reference to the customer | Yes |
| `lead` | Link (Lead) | Reference to the lead (if applicable) | No |
| `project` | Link (Project) | Reference to the project (Case II) | No |
| `measurement_date` | Date | Date when measurements were taken | Yes |
| `status` | Select | Draft, Submitted, Approved, Rejected | Yes |
| `measurement_method` | Select | Customer Provided, Tailor Assigned | Yes |

### Tailor Assignment Fields (Conditional)

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `assigned_tailor` | Link (Tailors) | Tailor assigned for measurement | Conditional |
| `site_visit_required` | Check | Whether site visit is needed | No |
| `visiting_charge` | Currency | Additional charge for site visit | No |
| `expected_measurement_date` | Date | Expected date for measurement completion | Conditional |
| `actual_measurement_date` | Date | Actual date when measurement was completed | No |

### Measurement Details (Child Table)

**Child Table Name:** `measurement_details`

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `area` | Data | Area where treatment will be installed (e.g., Living Room) | Yes |
| `product_type` | Select | Window Curtains, Roman Blinds, Blinds, Tracks/Rods | Yes |
| `layer` | Select | Front, Back | Conditional |
| `pattern` | Link (Pattern) | Pattern type (for curtains/blinds) | Conditional |
| `width` | Float | Width in inches | Conditional |
| `height` | Float | Height in inches | Conditional |
| `panels` | Int | Number of panels | Conditional |
| `adjust` | Float | Adjustment value | No |
| `quantity` | Float | Calculated or entered quantity | Yes |
| `fabric_type` | Link (Item) | Fabric item reference | Conditional |
| `lead_rope` | Link (Item) | Lead rope item (for curtains) | Conditional |
| `lining` | Link (Item) | Lining item reference | Conditional |
| `track_rod_type` | Link (Item) | Track/Rod type | Conditional |
| `design` | Link (Design) | Design for tracks/rods | Conditional |
| `selection` | Data | Material type or color (for blinds) | Conditional |
| `square_feet` | Float | Calculated square footage | Auto-calculated |
| `rate` | Currency | Rate per unit | Yes |
| `amount` | Currency | Total amount for this item | Auto-calculated |

### Summary Fields

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `total_amount` | Currency | Total amount for all items | Auto-calculated |
| `discount_percentage` | Float | Discount percentage | No |
| `discount_amount` | Currency | Discount amount | Auto-calculated |
| `net_amount` | Currency | Final amount after discount | Auto-calculated |
| `memo` | Text Editor | Special instructions or notes | No |

### Approval Fields

| Field Name | Field Type | Description | Mandatory |
|------------|-----------|-------------|-----------|
| `approved_by` | Link (User) | User who approved the measurement | No |
| `approval_date` | Datetime | Date and time of approval | No |
| `rejection_reason` | Text | Reason for rejection | Conditional |
| `customer_approval_status` | Select | Pending, Approved, Rejected | No |

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
1. **Draft** - Initial state when measurement sheet is created
2. **Submitted** - When salesperson submits the measurement sheet
3. **Approved** - When customer approves the measurements
4. **Rejected** - When customer rejects the measurements

### Status Transitions
- Draft → Submitted (by Salesperson)
- Submitted → Approved (by Salesperson as per customer response)
- Submitted → Rejected (by Salesperson as per customer response)

### Permissions Based on Status
- **Draft**: Can be edited and deleted
- **Submitted**: Read-only, awaiting approval
- **Approved**: Read-only, can create Sales Order
- **Rejected**: Read only

---

## Product Type Specific Fields

### Window Curtains
**Required Fields:**
- Layer (Front/Back)
- Pattern
- Width
- Height
- Panels
- Fabric Type
- Lead Rope
- Lining
- Track/Rod Type

**Auto-calculated Fields:**
- Quantity (based on width, height, panels, and pattern formula)
- Amount (quantity × fabric rate + accessories)

### Roman Blinds
**Required Fields:**
- Layer (Front/Back)
- Pattern
- Width
- Height
- Panels
- Fabric Type
- Lining

**Auto-calculated Fields:**
- Quantity (fabric meters)
- Square Feet
- Amount (based on square feet and rates)

### Blinds
**Required Fields:**
- Layer (Front/Back)
- Width
- Height
- Selection (material/color)

**Auto-calculated Fields:**
- Square Feet (width × height / 144)
- Amount (square feet × rate)

### Tracks/Rods
**Required Fields:**
- Design
- Width

**Auto-calculated Fields:**
- Amount (width × rate per unit)

---

## Calculation Formulas

### Window Curtains Quantity Calculation
```
Quantity (meters) = ((Width × Fullness Factor) + Adjust) × (Height + Hem Allowance) × Panels / 39.37
```
Where:
- Fullness Factor depends on pattern (e.g., French Pleated = 2.5, Tab Top = 2.0)
- Hem Allowance = 6-12 inches (configurable)
- 39.37 converts inches to meters

### Roman Blinds Square Feet Calculation
```
Square Feet = (Width × Height × Panels) / 144
```

### Blinds Square Feet Calculation
```
Square Feet = (Width × Height) / 144
```

### Amount Calculation
```
Amount = (Fabric Quantity × Fabric Rate) + (Lead Rope Quantity × Lead Rope Rate) + 
         (Lining Quantity × Lining Rate) + (Track/Rod Quantity × Track/Rod Rate)
```

---

## Measurement Collection Methods

### Method 1: Customer Provided Measurements
**Process:**
1. Salesperson selects "Customer Provided" as measurement method
2. Customer directly provides measurements (via phone, WhatsApp, or in-person)
3. Salesperson enters measurements into the system
4. No tailor assignment required
5. No visiting charge applicable

**Use Cases:**
- Customer has professional measurements
- Showroom delivery orders
- Simple curtain replacements

### Method 2: Tailor Assigned Measurement
**Process:**
1. Salesperson selects "Tailor Assigned" as measurement method
2. System shows tailor assignment fields
3. Salesperson assigns a tailor from the Tailors master
4. If site visit required, check "Site Visit Required" and enter visiting charge
5. Set expected measurement date
6. System sends notification to assigned tailor
7. Tailor visits customer site and takes measurements
8. Salesperson updates measurement sheet with actual measurements as per the tailor response

---

## Validation Rules

### Mandatory Field Validations
1. Customer must be selected
2. At least one measurement detail row must be present
3. For each measurement detail:
   - Area is mandatory
   - Product Type is mandatory
   - Product-specific mandatory fields must be filled
4. If measurement method is "Tailor Assigned":
   - Assigned Tailor is mandatory
   - Expected Measurement Date is mandatory

### Business Logic Validations
1. Width and Height must be greater than 0
2. Panels must be at least 1
3. Quantity must be greater than 0
4. Rate must be greater than 0
5. Discount percentage must be between 0 and 100
6. Status transitions must follow the defined workflow
7. Sales Order can only be created when status = "Approved"

### Conditional Field Validations
1. **Window Curtains**: Pattern, Fabric Type, Lead Rope, Lining, Track/Rod Type are mandatory
2. **Roman Blinds**: Pattern, Fabric Type, Lining are mandatory
3. **Blinds**: Selection is mandatory
4. **Tracks/Rods**: Design is mandatory

---

## Integration Points

### 1. Lead/Customer Integration
- Measurement Sheet can be created from Customer
- Customer details auto-populate from Lead/Customer master

### 2. Project Integration (Case II)
- Measurement Sheet linked to Project
- Measurement task created in Project task list
- Task completion updates project progress

### 3. Sales Order Integration
- "Create Sales Order" button available when status = "Approved"
- Sales Order items auto-populate from measurement details
- Item quantities and rates transfer to Sales Order

### 4. Item Master Integration
- Fabric Type, Lead Rope, Lining, Track/Rod Type link to Item master
- Rates fetch from Item Price List based on Customer Group
- SKU generation follows CATEGORY-VENDOR-RUNNINGNUMBER format

### 5. Tailor Integration
- Assigned Tailor links to measurement sheets
- Notification sent to tailor on assignment

### 6. Pricing Integration
- Base rates fetch from Item master
- Markup percentage applies based on Customer Group
- Price List assignment determines final rates

---

## User Permissions

### Salesperson Role
- Create new Measurement Sheet
- Edit Draft Measurement Sheet
- Submit Measurement Sheet
- View all Measurement Sheets
- Can able to approve/reject as per customer response

### Manager Role
- All Salesperson permissions
- Approve/Reject Measurement Sheet
- Override discount limits

---

## Notifications and Alerts

### Email/WhatsApp Notifications

1. **Tailor Assignment**
   - **Trigger**: When tailor is assigned to measurement sheet
   - **Recipient**: Assigned Tailor
   - **Content**: Customer details, expected date, site visit info

### Automated Notification: Assigned Contractor

- **Trigger Type**: Value Change
- **Field**: `assigned_contractor` (Link to `Employee`)
- **When**:
  - On new Measurement Sheet creation if `assigned_contractor` is set.
  - On updates when `assigned_contractor` value changes.
- **Action**: Send email to the assigned contractor (tailor).
- **Email Contents**:
  - Measurement Sheet ID
  - Customer and Project (if available)
  - Expected Measurement Date (if set)
  - Site Visit Required and Visiting Charge (if applicable)
- **Implementation**:
  - Server-side only; no UI changes.
  - Implemented in `fabric_sense/doctype/measurement_sheet/measurement_sheet.py`:
    - `after_insert()` sends on create when `assigned_contractor` is set.
    - `before_save()` checks `has_value_changed("assigned_contractor")` and sends on change.
    - `notify_assigned_contractor()` builds and sends the email via `frappe.sendmail()`.
    - `_get_contractor_email()` resolves recipient email from linked `User` or `Employee` emails.

> Note: Ensure outgoing Email Account is configured in the site for emails to be delivered.

---

## Best Practices

### For Salespersons
1. Always verify customer details before creating measurement sheet
2. Double-check measurements before submission
3. Add detailed notes in memo field for special requirements
4. Follow up with customer within 24 hours of submission
5. Keep customer informed about status changes

---

## Technical Implementation Notes

### Auto-naming Convention
```
MS-.YYYY.-.####
Example: MS-2024-0001, MS-2024-0002
```

### Child Table Naming
- measurement_details (for measurement line items)

### Server-side Validations
- Implement in `measurement_sheet.py` controller
- Override `validate()`, `before_save()`, `on_submit()` methods
- Add custom methods for calculations

### Unit Test Cases

- **Test: notify_assigned_contractor sends email**
  - Mock `_get_contractor_email()` to return a fixed email.
  - Mock `frappe.sendmail()` and assert it is called with expected recipients and subject.
  - Call `MeasurementSheet.notify_assigned_contractor()` directly.

- **Test: before_save triggers when assigned_contractor changes**
  - Set `assigned_contractor` on a new `Measurement Sheet` doc.
  - Mock `doc.has_value_changed("assigned_contractor")` to return `True`.
  - Mock `_get_contractor_email()` and `frappe.sendmail()`.
  - Call `MeasurementSheet.before_save()` and assert email is sent once.

### Client-side Scripts
- Implement in `measurement_sheet.js`
- Dynamic field visibility based on product type
- Real-time calculation updates
- Validation messages

---

### Reference Documents
- [Estimation Sheet Implementation Guide](./estimation_sheet_implementation_guide.md)
- [Case I Implementation](../case-i-implementation.md)
- [Case II Implementation](../case-ii-implementation.md)
- [Overview](../overview.md)

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Author**: Fabric Sense Development Team

# Measurement Sheet - Visual Diagrams

## 1. Doctype Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Measurement Sheet                         │
│                   (Parent Doctype)                           │
├─────────────────────────────────────────────────────────────┤
│ Basic Information                                            │
│  • naming_series: MS-.YYYY.-.####                           │
│  • customer: Link(Customer)                                  │
│  • lead: Link(Lead)                                          │
│  • project: Link(Project)                                    │
│  • measurement_date: Date                                    │
│  • status: Draft/Submitted/Approved/Rejected                │
│  • measurement_method: Customer Provided/Tailor Assigned    │
├─────────────────────────────────────────────────────────────┤
│ Tailor Assignment (conditional)                              │
│  • assigned_tailor: Link(Tailors)                           │
│  • expected_measurement_date: Date                           │
│  • site_visit_required: Check                                │
│  • visiting_charge: Currency                                 │
│  • actual_measurement_date: Date                             │
├─────────────────────────────────────────────────────────────┤
│ Measurement Details (Child Table)                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Measurement Detail (Child Table)              │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ • area: Data                                          │  │
│  │ • product_type: Window Curtains/Roman Blinds/...     │  │
│  │ • layer: Front/Back                                   │  │
│  │ • pattern: Link(Pattern)                              │  │
│  │ • width: Float                                        │  │
│  │ • height: Float                                       │  │
│  │ • panels: Int                                         │  │
│  │ • adjust: Float                                       │  │
│  │ • quantity: Float (calculated)                        │  │
│  │ • fabric_type: Link(Item)                             │  │
│  │ • lead_rope: Link(Item)                               │  │
│  │ • lining: Link(Item)                                  │  │
│  │ • track_rod_type: Link(Item)                          │  │
│  │ • design: Link(Design)                                │  │
│  │ • selection: Data                                     │  │
│  │ • square_feet: Float (calculated)                     │  │
│  │ • rate: Currency                                      │  │
│  │ • amount: Currency (calculated)                       │  │
│  └───────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│ Summary                                                      │
│  • total_amount: Currency (calculated)                      │
│  • discount_percentage: Float                                │
│  • discount_amount: Currency (calculated)                    │
│  • net_amount: Currency (calculated)                         │
│  • memo: Text Editor                                         │
├─────────────────────────────────────────────────────────────┤
│ Approval Details                                             │
│  • customer_approval_status: Pending/Approved/Rejected      │
│  • approved_by: Link(User)                                   │
│  • approval_date: Datetime                                   │
│  • rejection_reason: Text                                    │
└─────────────────────────────────────────────────────────────┘

## 4. Product Type Field Visibility

### Window Curtains
```
┌─────────────────────────────────┐
│ Window Curtains Selected        │
├─────────────────────────────────┤
│ ✓ Layer                         │
│ ✓ Pattern                       │
│ ✓ Width                         │
│ ✓ Height                        │
│ ✓ Panels                        │
│ ✓ Adjust                        │
│ ✓ Quantity (auto-calculated)    │
│ ✓ Fabric Type                   │
│ ✓ Lead Rope                     │
│ ✓ Lining                        │
│ ✓ Track/Rod Type                │
│ ✗ Design                        │
│ ✗ Selection                     │
│ ✗ Square Feet                   │
└─────────────────────────────────┘
```

### Roman Blinds
```
┌─────────────────────────────────┐
│ Roman Blinds Selected           │
├─────────────────────────────────┤
│ ✓ Layer                         │
│ ✓ Pattern                       │
│ ✓ Width                         │
│ ✓ Height                        │
│ ✓ Panels                        │
│ ✗ Adjust                        │
│ ✓ Quantity (auto-calculated)    │
│ ✓ Square Feet (auto-calculated) │
│ ✓ Fabric Type                   │
│ ✗ Lead Rope                     │
│ ✓ Lining                        │
│ ✗ Track/Rod Type                │
│ ✗ Design                        │
│ ✗ Selection                     │
└─────────────────────────────────┘
```

### Blinds
```
┌─────────────────────────────────┐
│ Blinds Selected                 │
├─────────────────────────────────┤
│ ✓ Layer                         │
│ ✗ Pattern                       │
│ ✓ Width                         │
│ ✓ Height                        │
│ ✗ Panels                        │
│ ✗ Adjust                        │
│ ✗ Quantity                      │
│ ✓ Square Feet (auto-calculated) │
│ ✗ Fabric Type                   │
│ ✗ Lead Rope                     │
│ ✗ Lining                        │
│ ✗ Track/Rod Type                │
│ ✗ Design                        │
│ ✓ Selection                     │
└─────────────────────────────────┘
```

### Tracks/Rods
```
┌─────────────────────────────────┐
│ Tracks/Rods Selected            │
├─────────────────────────────────┤
│ ✗ Layer                         │
│ ✗ Pattern                       │
│ ✓ Width                         │
│ ✗ Height                        │
│ ✗ Panels                        │
│ ✗ Adjust                        │
│ ✗ Quantity                      │
│ ✗ Square Feet                   │
│ ✗ Fabric Type                   │
│ ✗ Lead Rope                     │
│ ✗ Lining                        │
│ ✗ Track/Rod Type                │
│ ✓ Design                        │
│ ✗ Selection                     │
└─────────────────────────────────┘
```