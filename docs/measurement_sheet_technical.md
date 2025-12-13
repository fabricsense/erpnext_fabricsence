# Measurement Sheet - Technical Implementation

This document summarizes the implementation details for the Measurement Sheet doctypes (parent `Measurement Sheet`, child `Measurement Detail`), focusing on server/client logic, calculations, and integrations. Use this when onboarding engineers or debugging.

---

## Components
- Parent doctype: `Measurement Sheet`
- Child doctype: `Measurement Detail` (istable)
- Client script: `fabric_sense/doctype/measurement_sheet/measurement_sheet.js`
- Server code: `fabric_sense/doctype/measurement_sheet/measurement_sheet.py`, `fabric_sense/doctype/measurement_detail/measurement_detail.py`

---

## Field Highlights
### Measurement Sheet (parent)
- Required always: `customer`, `measurement_date`, `measurement_method`, `measurement_details` (table)
- Conditional: `assigned_contractor`, `expected_measurement_date`, `site_visit_required`, `visiting_charge`, `actual_measurement_date` (only when `measurement_method = Contractor Assigned`)
- Summary: `total_amount` (auto), `rejection_reason` (when `status = Rejected`)
- Status flow: Draft → Customer Approval Pending → Approved/Rejected

### Measurement Detail (child)
- Product types: `Window Curtains`, `Roman Blinds`, `Blinds`, `Tracks/Rods`
- Key inputs: `area`, `product_type`, dimensions (`width`, `height*`, `panels*`, `adjust*`, `square_feet*`)
- Items: fabric, lining, lead rope*, track/rod*, selection (Blinds)
- Service charges: `stitching_pattern`, `stitching_charge`, `fitting_type`, `fitting_charge`
- Outputs: quantities (fabric/lining, lead_rope_qty*, track_rod_qty*), amounts per component, row `amount`
(* visibility/requirement driven by product_type)

---

## Server-Side Logic
### measurement_sheet.py
- `validate()`: runs contractor assignment validation, child-row validation, then `calculate_totals()`.
- `validate_contractor_assignment()`: enforces contractor fields only when `measurement_method = Contractor Assigned`; `visiting_charge` required when `site_visit_required = 1`.
- `validate_measurement_details()`: ensures at least one row and delegates per-row validation.
- `validate_measurement_detail_row()`: product-specific mandatory checks (area, width, height unless Tracks/Rods; fabric or selection as appropriate).
- `calculate_totals()`: sums child `amount` values and adds `visiting_charge` if present; stores in `total_amount`.

### measurement_detail.py
- `validate()`: orchestrates calculations (amounts, square feet, fabric quantities, lead rope qty, track rod qty).
- `calculate_square_feet()`: `(width * height) / 144` for Roman Blinds/Blinds.
- `calculate_fabric_quantities()`: curtains use `((height + 16) * panels) / 38 + adjust`; Roman/Blinds mirror `square_feet`; sets `lining_qty`.
- `calculate_lead_rope_quantities()`: curtains only; `panels * 1.5`.
- `calculate_track_rod_quantities()`: curtains and Tracks/Rods; `(width / 12) * 2`.
- `calculate_amounts()`: fabric/lining/lead rope/track_rod amounts + `stitching_charge` + `fitting_charge`; Blinds add selection rate (Item Price selling → Item.standard_rate fallback); stored in row `amount`.

---

## Client-Side Logic (measurement_sheet.js)
- Centralizes all child handlers; `measurement_detail.js` kept as a stub.
- Debounced calculations (50ms) for row updates and totals.
- Totals: sum child `amount` + `visiting_charge`; recalculated on row changes, visiting charge, or site visit toggle.
- Field visibility/reqd toggles for contractor assignment and rejection reason.
- Item queries filtered by item groups (fabric, lining, lead rope, track/rod, blinds selection, stitching, fitting).
- Row calculations:
  - Square feet (Roman/Blinds), fabric qty (curtains, roman, blinds), lead_rope_qty (curtains), track_rod_qty (curtains/tracks), amounts with service charges, selection rate for Blinds.
  - Parent totals re-triggered after row amount updates.
- Stock check button: batch queries Bin for all items across rows, reports insufficient stock per row.

---

## Calculation Formulas (summary)
- Curtains:
  - `fabric_qty = ((height + 16) * panels) / 38 + adjust`
  - `lead_rope_qty = panels * 1.5`
  - `track_rod_qty = (width / 12) * 2`
  - `amount = fabric_amount + lining_amount + lead_rope_amount + track_rod_amount + stitching_charge + fitting_charge`
- Roman Blinds:
  - `square_feet = (width * height) / 144`
  - `fabric_qty = lining_qty = square_feet`
  - `amount = fabric_amount + lining_amount + stitching_charge + fitting_charge`
- Blinds:
  - `square_feet = (width * height) / 144`
  - `amount = selection_rate (Item Price→standard_rate) + fitting_charge`
- Tracks/Rods:
  - `track_rod_qty = (width / 12) * 2`
  - `amount = track_rod_amount + fitting_charge`
- Sheet total: `total_amount = sum(child.amount) + visiting_charge`

---

## Validation Summary
- Parent: customer, measurement_date, measurement_method, ≥1 child row; contractor fields only when assigned; visiting_charge required when site visit is checked; rejection_reason when status=Rejected.
- Child: area, product_type, width; height except for Tracks/Rods; fabric_selected for Curtains/Roman; selection for Blinds; positive quantities/rates enforced via calculations.

---

## Integration Points
- Items and Item Price (rates, item_group filters)
- Employee (assigned_contractor)
- Area, Pattern masters
- Stock check via `Bin` (batch query)
- Future: Sales Order handoff (not implemented here)

---

## Dev Notes
- Totals include visiting_charge both client- and server-side to prevent divergence.
- Item rate fetch favors Item Price (selling) then Item.standard_rate.
- Debounce timers prevent redundant recalcs; ensure no heavy async calls inside the tight loops.
- If adding new product types or charges, update both server calculators and client batch_calculate_row + amount logic.

