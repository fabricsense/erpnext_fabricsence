# Contractor Payment Flow

This note walks through how contractor payments are produced from the moment a Task is marked completed through to Payment Entry submission, with direct pointers to the code involved.

## 1) Task completion → calculate contractor amount
- `Task.before_save` hooks set in `hooks.py` ensure service rate and totals are populated and only react on the right status transitions. `handle_status_change_to_completed` runs when a Task moves from Working → Completed and computes `custom_service_rate`, `custom_service_charge`, and `custom_total_contractor_amount` (service rate × quantity + travelling charge) using service/contractor-specific rates from `Services` via `get_service_rate`.  

```111:180:fabric_sense/py/task.py
def handle_status_change_to_completed(doc, method=None):
    if doc.status != "Completed": return
    if doc.is_new(): return
    old_doc = doc.get_doc_before_save()
    if old_doc and old_doc.get("status") != "Working": return
    doc.actual_end_date = now_datetime().date()
    service_rate = get_service_rate(doc.custom_service, doc.custom_assigned_contractor)
    quantity = doc.custom_quantity or 1.0
    travelling_charge = doc.custom_travelling_charge or 0.0
    doc.custom_service_rate = service_rate
    doc.custom_service_charge = service_rate * quantity
    doc.custom_total_contractor_amount = doc.custom_service_charge + travelling_charge
```

## 2) Task update → create Contractor Payment History
- `Task.on_update` hook `create_contractor_payment_history` runs only when status becomes Completed. It skips if already created, if no contractor is assigned, or if amount is not > 0. When eligible, it inserts a `Contractor Payment History` (CPH) record with status `Unpaid` and zero `amount_paid`.

```182:260:fabric_sense/py/task.py
if doc.status != "Completed": return
old_doc = doc.get_doc_before_save()
if old_doc and old_doc.status == "Completed": return
if frappe.db.exists("Contractor Payment History", {"task": doc.name}): return
if not doc.custom_assigned_contractor: msgprint("No contractor…"); return
payment_amount = doc.custom_total_contractor_amount or 0
if payment_amount <= 0: msgprint("Payment amount not set…"); return
frappe.get_doc({
    "doctype": "Contractor Payment History",
    "task": doc.name,
    "project": doc.project,
    "contractor": doc.custom_assigned_contractor,
    "amount": payment_amount,
    "status": "Unpaid",
    "amount_paid": 0
}).insert(ignore_permissions=True)
```

## 3) Contractor Payment History doctype & UI
- Doctype definition: links a contractor (Employee), task, and project, with fields for `amount`, `amount_paid`, derived `balance` (ERPNext field formula), `payment_entry`, and `status` (`Unpaid`/`Partially Paid`/`Paid`).  
  - File: `fabric_sense/doctype/contractor_payment_history/contractor_payment_history.json`.
- Form script adds a `Make Payment` button when status is Unpaid; it creates a draft Payment Entry prefilled for the contractor and stores context in `sessionStorage` for the Payment Entry client script.  

```1:60:fabric_sense/doctype/contractor_payment_history/contractor_payment_history.js
if (frm.doc.status === "Unpaid" && !frm.is_new()) {
    frm.add_custom_button("Make Payment", () => frm.events.make_single_payment(frm))
         .addClass("btn-primary").prependTo(frm.page.page_actions);
}
// In make_single_payment:
payment_doc.payment_type = "Pay";
payment_doc.party_type = "Employee";
payment_doc.party = frm.doc.contractor;
payment_doc.paid_amount = frm.doc.balance;
payment_doc.received_amount = frm.doc.balance;
payment_doc.custom_contractor_payment_history = frm.doc.name;
sessionStorage.setItem("contractor_payment_ref", frm.doc.name);
// route to Payment Entry form
```

- List view script hides the default Add button and provides a **bulk payment** feature via the "Make Payment for Contractor" button. File: `contractor_payment_history_list.js`.

### Bulk Payment from List View

The list view allows users to pay multiple unpaid CPH records for a contractor in a single Payment Entry:

1. **Button**: "Make Payment for Contractor" button is added to the list view page actions.

2. **Dialog Flow**:
   - User selects a Contractor (Employee) from a Link field
   - On contractor selection, a server call fetches all unpaid/partially paid CPH records for that contractor
   - Records are displayed in a table showing: ID, Task, Project, Amount, Paid, Balance, Status
   - User can select individual records using checkboxes
   - "Selected Total" updates dynamically as records are checked/unchecked

3. **Server Method** (`get_unpaid_records_for_contractor`):
```python
# contractor_payment_history.py
@frappe.whitelist()
def get_unpaid_records_for_contractor(contractor):
    return frappe.get_all("Contractor Payment History",
        filters={"contractor": contractor, "status": ["in", ["Unpaid", "Partially Paid"]]},
        fields=["name", "task", "project", "amount", "amount_paid", "balance", "status"])
```

4. **Payment Entry Creation**:
   - On "Proceed to Payment", selected records are stored as JSON in `sessionStorage`
   - A new Payment Entry is created with:
     - `payment_type = "Pay"`
     - `party_type = "Employee"`
     - `party = contractor`
     - `paid_amount = sum of all selected balances`
   - The JSON array of selected records is stored in `custom_contractor_payment_records_json` field

```javascript
// contractor_payment_history_list.js
sessionStorage.setItem("contractor_payment_records", JSON.stringify(record_details));
frappe.set_route("Form", "Payment Entry", payment_doc.name);
```

## 4) Payment Entry customizations for contractor payouts
- Custom fields on Payment Entry (defined in `fabric_sense/custom/payment_entry.json`):
  - `custom_contractor_payment_history` (Link to CPH) - for single record backward compatibility
  - `custom_contractor_payment_records_json` (Long Text, hidden) - stores JSON array of multiple CPH record details for bulk payments
  - `custom_manager_approval_status` - manages approval flow (discount-related); enforced before submit

- Client script (`public/js/payment_entry.js`) enforces contractor context when a Payment Entry originates from CPH:
  - Forces `party_type = Employee`, repeatedly if needed, and sets `party` to the contractor from sessionStorage/CPH.
  - **Bulk Payment Handling**: Reads `contractor_payment_records` from sessionStorage and stores it in `custom_contractor_payment_records_json` field
  - Prefills `paid_from` with the first cash/bank account if empty.
  - Blocks submit if manager approval status is pending/rejected.

```javascript
// public/js/payment_entry.js - onload handler for bulk payments
if (contractorPaymentRecords) {
    let records = JSON.parse(contractorPaymentRecords);
    if (records && records.length > 0) {
        // Store JSON in the Long Text field
        frm.doc.custom_contractor_payment_records_json = contractorPaymentRecords;
        // Set first record for backward compatibility
        frm.set_value("custom_contractor_payment_history", records[0].name);
    }
}
```

## 5) Payment Entry server hooks → update CPH
- Hooks in `hooks.py`:
  - `Payment Entry.on_submit → update_contractor_payment_history`
  - `Payment Entry.on_cancel → revert_contractor_payment_history`
  - `Payment Entry.validate → set_manager_approval_status_for_deductions` (discount flow).

- Server logic in `fabric_sense/py/payment_entry.py`:

### Multi-Record Handling (Bulk Payments)
When `custom_contractor_payment_records_json` contains a JSON array of records:
  - On submit: Parse JSON, iterate through each record, update each CPH to `status = "Paid"`, set `amount_paid = amount` (full payment), link `payment_entry`
  - On cancel: Parse JSON, iterate through each record, revert each CPH to `status = "Unpaid"`, clear `amount_paid` and `payment_entry`

```python
# fabric_sense/py/payment_entry.py
def update_contractor_payment_history(doc, method=None):
    import json
    records_json = getattr(doc, 'custom_contractor_payment_records_json', None)
    
    if records_json:
        records = json.loads(records_json)
        for record in records:
            record_name = record.get('name') if isinstance(record, dict) else record
            cph_doc = frappe.get_doc("Contractor Payment History", record_name)
            cph_doc.status = "Paid"
            cph_doc.amount_paid = cph_doc.amount  # Pay full amount
            cph_doc.payment_entry = doc.name
            cph_doc.save(ignore_permissions=True)
        return
    
    # Fallback: single record via custom_contractor_payment_history
    if doc.custom_contractor_payment_history:
        cph = frappe.get_doc("Contractor Payment History", doc.custom_contractor_payment_history)
        cph.status = "Paid"; cph.amount_paid = doc.paid_amount; cph.payment_entry = doc.name
        cph.save(ignore_permissions=True)
```

### Single Record Handling (Backward Compatibility)
When only `custom_contractor_payment_history` is set (single record payment from CPH form):
  - On submit: Load CPH, mark `status = "Paid"`, copy `paid_amount`, link `payment_entry`
  - On cancel: Revert to `status = "Unpaid"`, clear `amount_paid` and `payment_entry`

## 6) Event wiring summary
- `hooks.py` binds Task and Payment Entry events:  
  - Task: `before_save` → rate/amount calculation; `on_update` → create CPH.  
  - Payment Entry: `validate` → approval status handling; `on_submit`/`on_cancel` → sync CPH.  
  - Files: `fabric_sense/hooks.py` for the mapping.

## End-to-end flow

### Single Payment Flow (from CPH Form)
1. Task moves from Working → Completed → contractor rate/amount computed and saved.  
2. Same Task update creates a `Contractor Payment History` record (Unpaid).  
3. From CPH form, user clicks **Make Payment** → new Payment Entry draft prefilled for the contractor (party_type forced to Employee).  
4. Payment Entry submit updates the linked CPH to Paid; cancel reverts to Unpaid.  
5. Manager approval status logic also runs on Payment Entry, but it is orthogonal to contractor linkage; submission is blocked until approved.

### Bulk Payment Flow (from CPH List View)
1. Multiple Tasks are completed for the same contractor → multiple CPH records created (Unpaid).
2. From CPH List View, user clicks **Make Payment for Contractor** button.
3. User selects the Contractor from the dialog → all unpaid CPH records for that contractor are displayed.
4. User selects one or more records using checkboxes → "Selected Total" shows cumulative balance.
5. User clicks **Proceed to Payment** → Payment Entry is created with:
   - Total amount = sum of selected balances
   - JSON of selected records stored in `custom_contractor_payment_records_json`
6. On Payment Entry submit:
   - Server iterates through the JSON array
   - **Each CPH record is updated individually** to `status = "Paid"`, `amount_paid = full amount`
   - All records link to the same Payment Entry
7. On Payment Entry cancel:
   - All linked CPH records are reverted to `status = "Unpaid"`

### Key Files
| File | Purpose |
|------|---------|
| `contractor_payment_history_list.js` | List view with bulk payment dialog |
| `contractor_payment_history.js` | Form view with single payment button |
| `contractor_payment_history.py` | Server method to fetch unpaid records |
| `public/js/payment_entry.js` | Client script to handle contractor context |
| `fabric_sense/py/payment_entry.py` | Server hooks to update CPH on submit/cancel |
| `custom/payment_entry.json` | Custom fields definition |

