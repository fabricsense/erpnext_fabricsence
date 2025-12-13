# Delivery Note Delivery Notification

## Overview
- **Trigger**: When a `Delivery Note` is submitted (`on_submit`).
- **Action**: Send a delivery confirmation email to the customer with delivery details.
- **Handler**: `fabric_sense/fabric_sense/py/delivery_note.py: send_customer_delivery_notification()`
- **Hook**: Defined in `fabric_sense/hooks.py` under `doc_events["Delivery Note"]["on_submit"]`.

## Email Content
- **Subject**: `Delivery Confirmation: <Delivery Note ID>`
- **Body**: Clean, responsive HTML table (same style philosophy as `measurement_sheet.py`), including:
  - Delivery Note ID
  - Customer name
  - Delivery date (`posting_date`)
  - Optional tracking details when present on the DN:
    - `tracking_number`
    - `carrier`
    - `lr_no`
    - `lr_date` (formatted)
    - `vehicle_no`
    - `tracking_url` (linkified)

## Recipient Resolution Priority
The recipient email is resolved by `_get_customer_email(doc)` with the following priority:
1. `Delivery Note.contact_person` → that `Contact.email_id`
2. `Delivery Note.contact_email`
3. `Customer.email_id`
4. `Customer.customer_primary_contact` → that `Contact.email_id`
5. Primary `Contact` linked to the `Customer` via Contact Links

If no email is found, the function logs an info/error entry titled: `Delivery Note: No recipient` and exits silently (non-blocking).

## Configuration Prerequisites
- Outgoing Email Account must be configured and enabled on the site.
- Scheduler/Workers must be running for queued email delivery.

## Process Flow
1. User submits `Delivery Note`.
2. Frappe hook triggers `send_customer_delivery_notification(doc, method="on_submit")`.
3. Handler resolves the recipient email using the priority above.
4. Handler builds the subject and HTML message.
5. Email is sent via `frappe.sendmail(...)` with `reference_doctype` and `reference_name` set to the DN.
6. Non-blocking: any errors are logged with `frappe.log_error()` and do not prevent submission.

## Troubleshooting
- **No email sent**: Ensure at least one of the recipient sources has a valid email.
- **Email stuck in queue**: Verify Email Queue, Outgoing Email Account, and scheduler/worker status.
- **HTML formatting**: Open the queued/sent email and verify the table renders. If needed, simplify inline styles.

## File References
- Hook registration: `fabric_sense/hooks.py`
- Handler implementation: `fabric_sense/fabric_sense/py/delivery_note.py`
- Related measurement sheet style reference: `fabric_sense/doctype/measurement_sheet/measurement_sheet.py`
