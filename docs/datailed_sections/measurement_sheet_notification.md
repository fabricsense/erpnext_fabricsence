# Measurement Sheet - Contractor Assignment Notification

## Overview
- **Trigger(s)**:
  - On create: `after_insert()` if `assigned_contractor` is set.
  - On update: `before_save()` if `assigned_contractor` value changes.
- **Action**: Send an email to the assigned contractor (tailor) with key job details.
- **Handler**: `fabric_sense/doctype/measurement_sheet/measurement_sheet.py: MeasurementSheet.notify_assigned_contractor()`

## Email Content
- **Subject**: `New Measurement Assignment - <Measurement Sheet ID>`
- **Body**: Modern, inline-styled HTML including:
  - Measurement ID
  - Customer name
  - Expected Measurement Date (if present)
  - Actual Measurement Date (if present)
  - Visiting Charge (if present)
  - Optional special instructions section

> The design matches the clean style used across the app's notifications (gradient header, readable tables).

## Recipient Resolution
Resolved by `_get_contractor_email(employee_id)` with priority:
1. Linked `User.email` from `Employee.user_id`
2. `Employee.company_email`
3. `Employee.personal_email`
4. `Employee.prefered_email`
5. `Employee.prefered_contact_email`

If no email is found, the function returns and does not block save.

## Duplicate Email Prevention
- `before_save()` is guarded to run only for updates: `not self.is_new()`.
- This prevents duplicate sends on create where both `after_insert()` and `before_save()` could execute in the same request.

## Process Flow
1. User creates or updates a Measurement Sheet and sets/changes `assigned_contractor`.
2. Controller triggers:
   - `after_insert()` → send once on create.
   - `before_save()` → send when `assigned_contractor` changes on updates.
3. `notify_assigned_contractor()` builds the subject and HTML body, resolves the recipient, and sends via `frappe.sendmail()`.
4. Errors are logged via `frappe.log_error()` and do not block saving.

## File References
- Notification implementation: `fabric_sense/doctype/measurement_sheet/measurement_sheet.py`
- Example of notification style: same file (`notify_assigned_contractor` method)

## Troubleshooting
- No email received: ensure the Employee has a resolvable email via the priority list above.
- Email formatting issues: the message uses inline CSS for better client compatibility.
- For environment issues, verify Email Account configuration and scheduler/worker status.
