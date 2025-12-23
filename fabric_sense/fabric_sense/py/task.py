import frappe # type: ignore
from frappe import _ # type: ignore
from frappe.utils import now_datetime, get_datetime, formatdate # type: ignore
from erpnext.projects.doctype.task.task import Task # type: ignore


def prefill_from_tailoring_sheet_and_service(doc, method=None):
    """
    Prefill service rate/charges even when Task status is Open.

    - If service + contractor are set and service rate is empty, fetch rate and compute charges.
    """
    # 1) Prefill UOM from Services if service is selected
    if hasattr(doc, "custom_service") and doc.custom_service:
        try:
            services_doc = frappe.get_doc("Services", doc.custom_service)
            if hasattr(services_doc, "uom") and services_doc.uom:
                # Try multiple possible field names for UOM
                uom_field_names = ["custom_unit", "unit", "custom_uom", "uom"]
                for field_name in uom_field_names:
                    if hasattr(doc, field_name) and not doc.get(field_name):
                        setattr(doc, field_name, services_doc.uom)
                        break
        except Exception as e:
            frappe.log_error(
                message=f"Error pre-filling UOM: {str(e)}",
                title="Task: UOM Prefill Error",
            )

    # 3) Prefill service rate & charges if data exists
    has_service = hasattr(doc, "custom_service") and doc.custom_service
    has_contractor = (
        hasattr(doc, "custom_assigned_contractor") and doc.custom_assigned_contractor
    )
    if has_service and has_contractor:
        service_rate = get_service_rate(
            service=doc.custom_service,
            contractor=doc.custom_assigned_contractor,
        )

        # Compute charges if fields exist
        quantity = (hasattr(doc, "custom_quantity") and doc.custom_quantity) or 1.0
        travelling_charge = (
            hasattr(doc, "custom_travelling_charge") and doc.custom_travelling_charge
        ) or 0.0

        service_charge = service_rate * quantity
        total_contractor_amount = service_charge + travelling_charge

        if hasattr(doc, "custom_service_rate"):
            doc.custom_service_rate = service_rate
        if hasattr(doc, "custom_service_charge"):
            doc.custom_service_charge = service_charge
        if hasattr(doc, "custom_total_contractor_amount"):
            doc.custom_total_contractor_amount = total_contractor_amount


def handle_status_change_to_working(doc, method=None):
    """
    Handle Task status change from Open to Working.

    Actions:
    1. Validate Tailoring Sheet is linked
    2. Set Actual Start Date if empty
    3. Material Request creation and Stock Entry opening handled in client script

    Args:
        doc: Task document
        method: Event method name
    """
    # Only process if status changed to "Working"
    if doc.status != "Working":
        return

    # Get old status from document before save
    old_status = None
    if not doc.is_new():
        old_doc = doc.get_doc_before_save()
        if old_doc:
            old_status = old_doc.get("status")

    # Only proceed if status changed from Open to Working (or if new document with Working status)
    if doc.is_new():
        # New document with Working status
        pass
    elif old_status == "Open":
        # Status changed from Open to Working
        pass
    else:
        # Status didn't change from Open, skip
        return

    # Validation: Check if Tailoring Sheet is linked
    tailoring_sheet = None
    if hasattr(doc, "custom_tailoring_sheet") and doc.custom_tailoring_sheet:
        tailoring_sheet = doc.custom_tailoring_sheet
    elif hasattr(doc, "tailoring_sheet") and doc.tailoring_sheet:
        tailoring_sheet = doc.tailoring_sheet

    if not tailoring_sheet:
        frappe.throw(
            _(
                "Please select a Tailoring Sheet before changing status to Working. Material Request and Stock Entry cannot be created without a Tailoring Sheet."
            )
        )

    # 1. Set Actual Start Date if the field exists and is empty
    if doc.meta.has_field("actual_start_date") and not doc.get("actual_start_date"):
        doc.actual_start_date = now_datetime().date()


def handle_status_change_to_completed(doc, method=None):
    """
    Handle Task status change from Working to Completed.

    Actions:
    1. Set Actual End Date
    2. Fetch Service Rate from Services doctype
    3. Calculate Service Charge = Service Rate × Quantity
    4. Calculate Total Contractor Amount = Service Charge + Travelling Charge
    5. Write results to Task fields

    Args:
        doc: Task document
        method: Event method name
    """
    # Only process if status changed to "Completed"
    if doc.status != "Completed":
        return

    # Get old status from document before save
    old_status = None
    if not doc.is_new():
        old_doc = doc.get_doc_before_save()
        if old_doc:
            old_status = old_doc.get("status")

    # Only proceed if status changed from Working to Completed
    if doc.is_new():
        # New document with Completed status - skip (shouldn't happen in normal flow)
        return
    elif old_status == "Working":
        # Status changed from Working to Completed
        pass
    else:
        # Status didn't change from Working, skip
        return

    # 1. Set Actual End Date if the field exists
    if doc.meta.has_field("actual_end_date"):
        doc.actual_end_date = now_datetime().date()

    # 2. Fetch Service Rate from Services doctype
    service_rate = 0.0
    service_charge = 0.0
    total_contractor_amount = 0.0

    if (
        hasattr(doc, "custom_service")
        and doc.custom_service
        and hasattr(doc, "custom_assigned_contractor")
        and doc.custom_assigned_contractor
    ):
        # Get service rate for the selected contractor and service
        service_rate = get_service_rate(
            service=doc.custom_service, contractor=doc.custom_assigned_contractor
        )

        # 3. Calculate Service Charge = Service Rate × Quantity
        quantity = (hasattr(doc, "custom_quantity") and doc.custom_quantity) or 1.0
        service_charge = service_rate * quantity

        # 4. Calculate Total Contractor Amount = Service Charge + Travelling Charge
        travelling_charge = (
            hasattr(doc, "custom_travelling_charge") and doc.custom_travelling_charge
        ) or 0.0
        total_contractor_amount = service_charge + travelling_charge

    # 5. Write results to Task fields
    if hasattr(doc, "custom_service_rate"):
        doc.custom_service_rate = service_rate
    if hasattr(doc, "custom_service_charge"):
        doc.custom_service_charge = service_charge
    if hasattr(doc, "custom_total_contractor_amount"):
        doc.custom_total_contractor_amount = total_contractor_amount


def create_contractor_payment_history(doc, method=None):
    """
    Create Contractor Payment History when task status changes to Completed.

    This function is called via hooks when a Task is saved.
    It checks if the status changed to "Completed" and creates a payment history record.

    Args:
        doc: Task document
        method: Event method name
    """
    # Only process if status is Completed
    if doc.status != "Completed":
        return

    # Check if status actually changed to Completed
    if not doc.is_new():
        old_doc = doc.get_doc_before_save()
        if old_doc and old_doc.status == "Completed":
            # Status was already Completed, no need to create payment history again
            return

    # Check if payment record already exists for this task
    existing = frappe.db.exists("Contractor Payment History", {"task": doc.name})

    if existing:
        return

    # Check if contractor is assigned
    if not doc.custom_assigned_contractor:
        frappe.msgprint(
            _("No contractor assigned to this task. Payment history not created."),
            indicator="orange",
            alert=True,
        )
        return

    # Check if payment amount is set
    payment_amount = doc.custom_total_contractor_amount or 0

    if not payment_amount or payment_amount <= 0:
        frappe.msgprint(
            _("Payment amount not set for this task. Payment history not created."),
            indicator="orange",
            alert=True,
        )
        return

    # Create payment history record
    try:
        payment_history = frappe.get_doc(
            {
                "doctype": "Contractor Payment History",
                "task": doc.name,
                "project": doc.project,
                "contractor": doc.custom_assigned_contractor,
                "amount": payment_amount,
                "status": "Unpaid",
                "amount_paid": 0,
                "payable_account": doc.custom_payable_account
            }
        )

        payment_history.insert(ignore_permissions=True)
        frappe.db.commit()

        frappe.msgprint(
            _("Contractor Payment History created: {0}").format(
                frappe.get_desk_link("Contractor Payment History", payment_history.name)
            ),
            indicator="green",
            alert=True,
        )

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(), "Create Contractor Payment History Failed"
        )
        frappe.msgprint(
            _("Failed to create payment history: {0}").format(str(e)),
            indicator="red",
            alert=True,
        )


def create_journal_entry_for_completed_task(doc, method=None):
    """
    Create and submit Journal Entry when task status changes to Completed.

    This function is called via hooks when a Task is saved.
    It checks if the status changed to "Completed" and creates a journal entry record
    with debit to expense account and credit to payable account (contractor liability).
    The Journal Entry is automatically submitted.

    Args:
        doc: Task document
        method: Event method name
    """
    # Only process if status is Completed
    if doc.status != "Completed":
        return

    # Check if status actually changed to Completed
    if not doc.is_new():
        old_doc = doc.get_doc_before_save()
        if old_doc and old_doc.status == "Completed":
            # Status was already Completed, no need to create journal entry again
            return

    # Check if journal entry already exists for this task
    existing = frappe.db.exists("Journal Entry", {"custom_task": doc.name})

    if existing:
        return

    # Check if contractor is assigned
    if not doc.custom_assigned_contractor:
        frappe.msgprint(
            _("No contractor assigned to this task. Journal Entry not created."),
            indicator="orange",
            alert=True,
        )
        return

    # Check if payment amount is set
    payment_amount = doc.custom_total_contractor_amount or 0

    if not payment_amount or payment_amount <= 0:
        frappe.msgprint(
            _("Payment amount not set for this task. Journal Entry not created."),
            indicator="orange",
            alert=True,
        )
        return

    # Get payable account from task or use default
    payable_account = doc.custom_payable_account
    if not payable_account:
        frappe.msgprint(
            _("Payable account not set for this task. Journal Entry not created."),
            indicator="orange",
            alert=True,
        )
        return
    
    expense_account = doc.custom_expense_account
    if not expense_account:
        frappe.msgprint(
            _("Expense account not set for this task. Journal Entry not created."),
            indicator="orange",
            alert=True,
        )
        return


    # Get company from task
    company = doc.company if hasattr(doc, "company") and doc.company else frappe.defaults.get_user_default("Company")
    
    if not company:
        frappe.msgprint(
            _("Company not found. Journal Entry not created."),
            indicator="orange",
            alert=True,
        )
        return

    # Create journal entry record
    try:
        journal_entry = frappe.get_doc(
            {
                "doctype": "Journal Entry",
                "company": company,
                "posting_date": frappe.utils.today(),
                "custom_task": doc.name,
                "user_remark": f"Journal Entry for Task {doc.name} - {doc.subject or ''}",
                "accounts": [
                    {
                        "account": expense_account,
                        "debit_in_account_currency": payment_amount,
                        "credit_in_account_currency": 0,
                    },
                    {
                        "account": payable_account,
                        "party_type": "Employee",
                        "party": doc.custom_assigned_contractor,
                        "debit_in_account_currency": 0,
                        "credit_in_account_currency": payment_amount,
                    }
                ]
            }
        )

        journal_entry.insert(ignore_permissions=True)
        
        # Submit the Journal Entry automatically
        journal_entry.submit()
        frappe.db.commit()

        frappe.msgprint(
            _("Journal Entry created and submitted: {0}").format(
                frappe.get_desk_link("Journal Entry", journal_entry.name)
            ),
            indicator="green",
            alert=True,
        )

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(), "Create Journal Entry for Task Failed"
        )
        frappe.msgprint(
            _("Failed to create journal entry: {0}").format(str(e)),
            indicator="red",
            alert=True,
        )


def get_service_rate(service, contractor, show_message=True):
    """
    Get service rate from Services doctype for a specific contractor and service.

    Args:
        service (str): Service name
        contractor (str): Contractor (Employee) name
        show_message (bool): Whether to show error messages (default: True)

    Returns:
        float: Service rate, or 0.0 if not found
    """
    try:
        # Get the Services document
        services_doc = frappe.get_doc("Services", service)

        # Search for the contractor in the contractors child table
        for contractor_row in services_doc.contractors:
            if contractor_row.contractor == contractor:
                return float(contractor_row.rate or 0.0)

        # If contractor not found in the service, return 0
        if show_message:
            frappe.msgprint(
                _("Service rate not found for contractor {0} in service {1}").format(
                    contractor, service
                ),
                indicator="orange",
                alert=True,
            )
        return 0.0

    except frappe.DoesNotExistError:
        if show_message:
            frappe.msgprint(
                _("Service {0} not found").format(service),
                indicator="orange",
                alert=True,
            )
        return 0.0
    except Exception as e:
        frappe.log_error(
            message=f"Error fetching service rate: {str(e)}",
            title="Task: Service Rate Error",
        )
        return 0.0


@frappe.whitelist()
def get_service_rate_and_calculate_charges(
    service, contractor, quantity=1.0, travelling_charge=0.0
):
    """
    Get service rate and calculate charges for client-side use.

    Args:
        service (str): Service name
        contractor (str): Contractor (Employee) name
        quantity (float): Quantity (default: 1.0)
        travelling_charge (float): Travelling charge (default: 0.0)

    Returns:
        dict: Contains service_rate, service_charge, total_contractor_amount, and uom
    """
    service_rate = 0.0
    service_charge = 0.0
    total_contractor_amount = 0.0
    uom = None

    if service:
        try:
            # Get UOM from Services doctype
            services_doc = frappe.get_doc("Services", service)
            if hasattr(services_doc, "uom") and services_doc.uom:
                uom = services_doc.uom
        except Exception as e:
            frappe.log_error(
                message=f"Error fetching UOM from Services: {str(e)}",
                title="Task: UOM Fetch Error",
            )

    if service and contractor:
        # Don't show messages when called from client-side (frequent calls)
        service_rate = get_service_rate(service, contractor, show_message=False)
        service_charge = service_rate * float(quantity or 1.0)
        total_contractor_amount = service_charge + float(travelling_charge or 0.0)

    return {
        "service_rate": service_rate,
        "service_charge": service_charge,
        "total_contractor_amount": total_contractor_amount,
        "uom": uom,
    }


def is_service_item(item_code):
    """
    Check if an item should be excluded from Material Request.
    Items are excluded if their parent item group is "Stitching" or "Labour".

    Args:
        item_code (str): Item code to check

    Returns:
        bool: True if item should be excluded (is a service item), False otherwise
    """
    try:
        # Get item's item_group
        item_group = frappe.db.get_value("Item", item_code, "item_group")
        if not item_group:
            return False

        # Check if item_group is "Stitching" or "Labour" (root level)
        if item_group in ["Stitching", "Labour"]:
            return True

        # Check if item_group starts with "Stitching/" or "Labour/" (child groups stored as paths)
        if item_group.startswith("Stitching/") or item_group.startswith("Labour/"):
            return True

        # Check parent_item_group if item_group is a child
        # In ERPNext, hierarchical item groups can be stored as "Parent/Child"
        # or we can check the parent_item_group field of the Item Group
        try:
            # Try to get Item Group by the full path first
            if frappe.db.exists("Item Group", item_group):
                item_group_doc = frappe.get_doc("Item Group", item_group)
                if (
                    hasattr(item_group_doc, "parent_item_group")
                    and item_group_doc.parent_item_group
                ):
                    parent_group = item_group_doc.parent_item_group
                    if parent_group in ["Stitching", "Labour"]:
                        return True
        except Exception:
            # If getting Item Group fails, try to extract parent from path
            # For paths like "Stitching/Curtain Stitching", check if first part is Stitching or Labour
            if "/" in item_group:
                parent_from_path = item_group.split("/")[0]
                if parent_from_path in ["Stitching", "Labour"]:
                    return True

        return False
    except Exception:
        # If there's any error checking, don't exclude the item
        return False


def extract_items_from_tailoring_sheet(tailoring_sheet_name):
    """
    Extract items from Tailoring Sheet measurement_details child table.

    Extracts material items (fabric, lining, lead_rope, track_rod) and aggregates
    quantities for same items across multiple rows.
    Service items (parent item group is "Stitching" or "Labour") are excluded.

    Args:
        tailoring_sheet_name (str): Name of the Tailoring Sheet

    Returns:
        list: List of item dictionaries with item_code and qty
        Format: [{"item_code": "...", "qty": ...}, ...]

    Raises:
        frappe.ValidationError: If Tailoring Sheet has no items
    """
    try:
        # Fetch Tailoring Sheet document
        tailoring_sheet = frappe.get_doc("Tailoring Sheet", tailoring_sheet_name)

        # Dictionary to store aggregated quantities by item_code
        item_quantities = {}

        # Validate measurement_details exists and has items
        if (
            not hasattr(tailoring_sheet, "measurement_details")
            or not tailoring_sheet.measurement_details
        ):
            frappe.throw(
                _(
                    "Tailoring Sheet has no items to create Material Request. Please add items in measurement_details."
                )
            )

        # Extract items from measurement_details
        for row in tailoring_sheet.measurement_details:
            # Fabric Selected
            if (
                row.fabric_selected
                and row.final_fabric_quantity
                and row.final_fabric_quantity > 0
            ):
                if row.fabric_selected not in item_quantities:
                    item_quantities[row.fabric_selected] = 0.0
                item_quantities[row.fabric_selected] += float(row.final_fabric_quantity)

            # Lining
            if (
                row.lining
                and row.final_lining_quantity
                and row.final_lining_quantity > 0
            ):
                if row.lining not in item_quantities:
                    item_quantities[row.lining] = 0.0
                item_quantities[row.lining] += float(row.final_lining_quantity)

            # Lead Rope
            if row.lead_rope and row.lead_rope_qty and row.lead_rope_qty > 0:
                if row.lead_rope not in item_quantities:
                    item_quantities[row.lead_rope] = 0.0
                item_quantities[row.lead_rope] += float(row.lead_rope_qty)

            # Track/Rod
            if row.track_rod and row.track_rod_qty and row.track_rod_qty > 0:
                if row.track_rod not in item_quantities:
                    item_quantities[row.track_rod] = 0.0
                item_quantities[row.track_rod] += float(row.track_rod_qty)

        # Convert to list of dictionaries, excluding service items
        items = []
        for item_code, qty in item_quantities.items():
            # Skip service items (parent item group is "Stitching" or "Labour")
            if not is_service_item(item_code):
                items.append({"item_code": item_code, "qty": qty})

        # Validate that we have at least one item
        if not items:
            frappe.throw(
                _(
                    "Tailoring Sheet has no items to create Material Request. Please ensure measurement_details contains items with quantities."
                )
            )

        return items

    except frappe.DoesNotExistError:
        frappe.throw(_("Tailoring Sheet {0} not found").format(tailoring_sheet_name))
    except Exception as e:
        frappe.log_error(
            message=f"Error extracting items from Tailoring Sheet: {str(e)}",
            title="Task: Extract Items Error",
        )
        frappe.throw(
            _("Error extracting items from Tailoring Sheet: {0}").format(str(e))
        )


@frappe.whitelist()
def get_or_create_material_request_for_task(tailoring_sheet):
    """
    Get or create Material Request (Issue type) for Tailoring Sheet.

    - Checks if Material Request exists for the Tailoring Sheet
    - If exists and submitted: Returns Material Request details
    - If exists but not submitted: Throws validation error
    - If not exists: Creates and submits Material Request automatically

    Args:
        tailoring_sheet (str): Tailoring Sheet name

    Returns:
        dict: Contains material_request_name, items list, and created flag
        Format: {
            "material_request_name": "...",
            "items": [...],
            "created": True/False
        }
    """
    try:
        # Validation: Check if tailoring_sheet is provided
        if not tailoring_sheet:
            frappe.throw(_("Tailoring Sheet is required to create Material Request"))

        # Check for existing Material Request
        material_request = frappe.db.get_value(
            "Material Request",
            {
                "custom_tailoring_sheet": tailoring_sheet,
                "material_request_type": "Material Issue",
                "docstatus": ["!=", 2],  # Not cancelled
            },
            ["name", "docstatus"],
            as_dict=True,
        )

        # If Material Request exists
        if material_request:
            # Check if it's submitted
            if material_request.docstatus == 1:
                # Material Request is submitted, return it
                mr_doc = frappe.get_doc("Material Request", material_request.name)
                items = []

                for item in mr_doc.items:
                    items.append(
                        {
                            "item_code": item.item_code,
                            "qty": item.qty,
                            "uom": item.uom,
                            "item_name": item.item_name,
                            "description": item.description,
                            "name": item.name,  # Row name for linking
                        }
                    )

                return {
                    "material_request_name": material_request.name,
                    "items": items,
                    "created": False,
                }
            else:
                # Material Request exists but is not submitted
                frappe.throw(
                    _(
                        "Material Request {0} exists but is not submitted. Please submit it before continuing."
                    ).format(material_request.name)
                )

        # Material Request does not exist, create it
        # Extract items from Tailoring Sheet
        items = extract_items_from_tailoring_sheet(tailoring_sheet)

        # Create Material Request
        mr_doc = frappe.get_doc(
            {
                "doctype": "Material Request",
                "material_request_type": "Material Issue",
                "custom_tailoring_sheet": tailoring_sheet,
                "transaction_date": frappe.utils.today(),
                "schedule_date": frappe.utils.today(),
            }
        )

        # Add items to Material Request
        for item in items:
            # Get item details for UOM
            item_doc = frappe.get_doc("Item", item["item_code"])
            default_uom = (
                item_doc.stock_uom
                if hasattr(item_doc, "stock_uom") and item_doc.stock_uom
                else "Nos"
            )

            mr_doc.append(
                "items",
                {
                    "item_code": item["item_code"],
                    "qty": item["qty"],
                    "uom": default_uom,
                    "schedule_date": frappe.utils.today(),
                },
            )

        # Save Material Request
        mr_doc.insert()

        # Submit Material Request automatically
        mr_doc.submit()

        # Prepare items list for return
        items_list = []
        for item in mr_doc.items:
            items_list.append(
                {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "uom": item.uom,
                    "item_name": item.item_name,
                    "description": item.description,
                    "name": item.name,  # Row name for linking
                }
            )

        return {
            "material_request_name": mr_doc.name,
            "items": items_list,
            "created": True,
        }

    except frappe.ValidationError:
        # Re-raise validation errors
        raise
    except Exception as e:
        frappe.log_error(
            message=f"Error in get_or_create_material_request_for_task: {str(e)}",
            title="Task: MR Creation Error",
        )
        frappe.throw(_("Error creating Material Request: {0}").format(str(e)))


@frappe.whitelist()
def get_material_request_items_for_stock_entry(tailoring_sheet):
    """
    Get Material Request items for Stock Entry creation with remaining quantities.

    Finds ALL Material Requests with type "Material Issue" or "Purchase" linked to the Tailoring Sheet via custom_tailoring_sheet.
    Aggregates quantities for the same items across all Material Requests.
    Fetches existing Stock Entry records for this tailoring sheet and calculates remaining quantities.
    Returns only items with remaining quantities > 0.

    Args:
        tailoring_sheet (str): Tailoring Sheet name

    Returns:
        dict: Contains material_request_name, items list (remaining quantities only), docstatus, and message
    """
    try:
        # Get all Material Requests (type "Material Issue" or "Purchase") linked to this Tailoring Sheet
        # Prioritize submitted MRs, but include drafts if no submitted ones exist
        submitted_mrs = frappe.get_all(
            "Material Request",
            filters={
                "custom_tailoring_sheet": tailoring_sheet,
                "material_request_type": ["in", ["Material Issue", "Purchase"]],
                "docstatus": 1,  # Submitted
            },
            fields=["name", "docstatus"],
            order_by="creation desc",
        )

        draft_mrs = frappe.get_all(
            "Material Request",
            filters={
                "custom_tailoring_sheet": tailoring_sheet,
                "material_request_type": ["in", ["Material Issue", "Purchase"]],
                "docstatus": 0,  # Draft
            },
            fields=["name", "docstatus"],
            order_by="creation desc",
        )

        # Use submitted MRs if available, otherwise use draft MRs
        material_requests = submitted_mrs if submitted_mrs else draft_mrs

        if not material_requests:
            return {
                "material_request_name": None,
                "items": [],
                "docstatus": None,
                "message": "No Material Request (Material Issue or Purchase) found for this Tailoring Sheet",
            }

        # Dictionary to store aggregated items by item_code
        # Structure: {item_code: {qty: sum, uom: value, stock_uom: value, item_name: value, description: value, mr_names: [list]}}
        aggregated_items = {}
        all_mr_names = []
        all_submitted = True

        # Process all Material Requests and aggregate items
        for mr in material_requests:
            all_mr_names.append(mr.name)
            if mr.docstatus != 1:
                all_submitted = False

            # Get Material Request document to access items
            mr_doc = frappe.get_doc("Material Request", mr.name)

            for item in mr_doc.items:
                item_code = item.item_code

                # Initialize item in aggregated_items if not exists
                if item_code not in aggregated_items:
                    # Get stock_uom from Item master
                    stock_uom = None
                    try:
                        item_doc = frappe.get_doc("Item", item_code)
                        stock_uom = (
                            item_doc.stock_uom
                            if hasattr(item_doc, "stock_uom") and item_doc.stock_uom
                            else item.uom
                        )
                    except Exception:
                        # If item not found or error, use uom from Material Request as fallback
                        stock_uom = item.uom

                    aggregated_items[item_code] = {
                        "qty": 0.0,
                        "uom": item.uom,
                        "stock_uom": stock_uom,
                        "item_name": item.item_name,
                        "description": item.description,
                        "mr_names": [],
                    }

                # Aggregate quantity
                aggregated_items[item_code]["qty"] += float(item.qty)
                # Store MR name for reference (use first occurrence for metadata)
                if mr.name not in aggregated_items[item_code]["mr_names"]:
                    aggregated_items[item_code]["mr_names"].append(mr.name)

        # Fetch existing Stock Entry records for this tailoring sheet
        # Look for Stock Entries that have custom_tailoring_sheet field or are linked via Material Request
        issued_quantities = {}

        # Method 1: Direct link via custom_tailoring_sheet field (if exists)
        try:
            stock_entries_direct = frappe.get_all(
                "Stock Entry",
                filters={
                    "custom_tailoring_sheet": tailoring_sheet,
                    "stock_entry_type": "Material Issue",
                    "docstatus": 1,  # Submitted only
                },
                fields=["name"],
            )

            for se in stock_entries_direct:
                se_doc = frappe.get_doc("Stock Entry", se.name)
                for item in se_doc.items:
                    item_code = item.item_code
                    if item_code not in issued_quantities:
                        issued_quantities[item_code] = 0.0
                    issued_quantities[item_code] += float(item.qty or 0)
        except Exception:
            # custom_tailoring_sheet field might not exist, continue with other methods
            pass

        # Method 2: Link via Material Request reference
        try:
            # Get Stock Entries that reference our Material Requests
            mr_names_list = [mr.name for mr in material_requests]
            if mr_names_list:
                # Find Stock Entries that reference any of our Material Requests
                stock_entries_mr = frappe.get_all(
                    "Stock Entry",
                    filters={
                        "material_request": ["in", mr_names_list],
                        "stock_entry_type": "Material Issue",
                        "docstatus": 1,  # Submitted only
                    },
                    fields=["name", "material_request"],
                )

                for se in stock_entries_mr:
                    se_doc = frappe.get_doc("Stock Entry", se.name)
                    for item in se_doc.items:
                        item_code = item.item_code
                        if item_code not in issued_quantities:
                            issued_quantities[item_code] = 0.0
                        issued_quantities[item_code] += float(item.qty or 0)
        except Exception as e:
            frappe.log_error(
                message=f"Error fetching Stock Entries via Material Request: {str(e)}",
                title="Task: Stock Entry Fetch Error",
            )

        # Calculate remaining quantities and filter items
        remaining_items = []
        for item_code, data in aggregated_items.items():
            requested_qty = data["qty"]
            issued_qty = issued_quantities.get(item_code, 0.0)
            remaining_qty = requested_qty - issued_qty

            # Only include items with remaining quantity > 0
            if remaining_qty > 0:
                remaining_items.append(
                    {
                        "item_code": item_code,
                        "qty": remaining_qty,
                        "requested_qty": requested_qty,
                        "issued_qty": issued_qty,
                        "uom": data["uom"],
                        "stock_uom": data["stock_uom"],
                        "item_name": data["item_name"],
                        "description": data["description"],
                        "name": None,  # Cannot link to single MR row when aggregated from multiple MRs
                    }
                )

        # Determine material_request_name (comma-separated if multiple, or single name)
        if len(all_mr_names) == 1:
            material_request_name = all_mr_names[0]
        else:
            material_request_name = ", ".join(all_mr_names)

        # Determine docstatus (1 if all submitted, 0 if any draft)
        docstatus = 1 if all_submitted else 0

        # Prepare message based on remaining items
        message = None
        if not all_submitted:
            message = "Some Material Requests are not submitted. Please submit them before creating Stock Entry."
        elif not remaining_items:
            message = (
                "All Material Request items have already been issued via Stock Entries."
            )

        return {
            "material_request_name": material_request_name,
            "items": remaining_items,
            "docstatus": docstatus,
            "message": message,
            "total_items_requested": len(aggregated_items),
            "remaining_items_count": len(remaining_items),
        }

    except Exception as e:
        frappe.log_error(
            message=f"Error fetching Material Request items: {str(e)}",
            title="Task: MR Items Fetch Error",
        )
        return {"material_request_name": None, "items": [], "error": str(e)}


@frappe.whitelist()
def get_contractors_for_service(service):
    """
    Get list of contractors (employees) for a given service.

    Args:
        service (str): Service name

    Returns:
        list: List of contractor (employee) names
    """
    try:
        if not service:
            return []

        # Get the Services document
        services_doc = frappe.get_doc("Services", service)

        # Extract contractor names from the contractors child table
        contractors = []
        if hasattr(services_doc, "contractors") and services_doc.contractors:
            for contractor_row in services_doc.contractors:
                if contractor_row.contractor:
                    contractors.append(contractor_row.contractor)

        return contractors

    except frappe.DoesNotExistError:
        return []
    except Exception as e:
        frappe.log_error(
            message=f"Error fetching contractors for service: {str(e)}",
            title="Task: Get Contractors Error",
        )
        return []


@frappe.whitelist()
def get_latest_tailoring_sheet_for_project(project):
    """
    Get the most recent Tailoring Sheet for a given Project.

    Args:
        project (str): Project name

    Returns:
        str: Name of the most recent Tailoring Sheet, or None if not found
    """
    try:
        if not project:
            return None

        # Query for the most recent Tailoring Sheet linked to this project
        tailoring_sheet = frappe.db.get_value(
            "Tailoring Sheet", {"project": project}, "name", order_by="creation desc"
        )

        return tailoring_sheet

    except Exception as e:
        frappe.log_error(
            message=f"Error fetching latest tailoring sheet for project: {str(e)}",
            title="Task: Get Latest Tailoring Sheet Error",
        )
        return None


def notify_assigned_contractor(doc, method=None):
    """
    Send an email to the assigned contractor when custom_assigned_contractor is set or changed.

    Args:
        doc: Task document
        method: Event method name
    """
    try:
        # Only process if contractor is assigned and field changed (for updates)
        if not doc.custom_assigned_contractor:
            return

        # For updates, only send if field changed
        if not doc.is_new():
            old_doc = doc.get_doc_before_save()
            if (
                old_doc
                and old_doc.get("custom_assigned_contractor")
                == doc.custom_assigned_contractor
            ):
                # Field didn't change, skip notification
                return

        # Get contractor email
        recipient = _get_contractor_email(doc.custom_assigned_contractor)
        if not recipient:
            return

        # Get contractor name for personalization
        contractor_name = (
            frappe.db.get_value(
                "Employee", doc.custom_assigned_contractor, "employee_name"
            )
            or "there"
        )

        # Build subject
        subject = f"New Task Assignment - {doc.subject or doc.name or ''}"

        # Prepare data rows
        rows = []

        # Task Name (subject)
        if doc.subject:
            rows.append(
                f"""
                <tr>
                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
                        <strong style="color: #374151;">Task Name</strong>
                    </td>
                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                        <span style="font-family: 'Courier New', monospace; color: #1f2937; font-weight: 600;">{frappe.utils.escape_html(doc.subject)}</span>
                    </td>
                </tr>
            """
            )

        # Task ID
        if doc.name:
            rows.append(
                f"""
                <tr>
                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
                        <strong style="color: #374151;">Task ID</strong>
                    </td>
                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                        <span style="color: #1f2937;">{frappe.utils.escape_html(doc.name)}</span>
                    </td>
                </tr>
            """
            )

        # Project
        if doc.project:
            project_name = (
                frappe.db.get_value("Project", doc.project, "project_name")
                or doc.project
            )
            rows.append(
                f"""
                <tr>
                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
                        <strong style="color: #374151;">Project</strong>
                    </td>
                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                        <span style="color: #1f2937;">{frappe.utils.escape_html(project_name)}</span>
                    </td>
                </tr>
            """
            )

        # Priority
        if doc.priority:
            rows.append(
                f"""
                <tr>
                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
                        <strong style="color: #374151;">Priority</strong>
                    </td>
                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                        <span style="color: #1f2937;">{frappe.utils.escape_html(doc.priority)}</span>
                    </td>
                </tr>
            """
            )

        # Expected Start Date
        if getattr(doc, "exp_start_date", None):
            rows.append(
                f"""
                <tr>
                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
                        <strong style="color: #374151;">📅 Expected Start Date</strong>
                    </td>
                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                        <span style="color: #1f2937; font-weight: 600;">{formatdate(doc.exp_start_date)}</span>
                    </td>
                </tr>
            """
            )

        # Expected End Date
        if getattr(doc, "exp_end_date", None):
            rows.append(
                f"""
                <tr>
                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb; background-color: #f9fafb;">
                        <strong style="color: #374151;">📅 Expected End Date</strong>
                    </td>
                    <td style="padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                        <span style="color: #1f2937; font-weight: 600;">{formatdate(doc.exp_end_date)}</span>
                    </td>
                </tr>
            """
            )

        rows_html = "".join(rows)

        # Build the complete HTML message with modern styling (same as Measurement Sheet)
        message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', 'Roboto', 'Helvetica Neue', Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <!-- Header Card -->
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px 12px 0 0; padding: 32px 24px; text-align: center;">
                        <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;">New Task Assignment</h1>
                        <p style="margin: 8px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">You have been assigned to a new task</p>
                    </div>
                    
                    <!-- Main Content Card -->
                    <div style="background-color: white; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
                        <!-- Greeting -->
                        <div style="padding: 24px 24px 16px;">
                            <p style="margin: 0; font-size: 16px; color: #1f2937; line-height: 1.6;">
                                Hello <strong style="color: #667eea;">{frappe.utils.escape_html(contractor_name)}</strong>,
                            </p>
                            <p style="margin: 12px 0 0; font-size: 15px; color: #4b5563; line-height: 1.6;">
                                You have been assigned to a new task. Please review the details below and proceed accordingly.
                            </p>
                        </div>
                        
                        <!-- Details Table -->
                        <div style="padding: 0 24px 24px;">
                            <table style="width: 100%; border-collapse: collapse; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                                <tbody>
                                    {rows_html}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        """

        frappe.sendmail(
            recipients=[recipient],
            subject=subject,
            message=message,
            reference_doctype=doc.doctype,
            reference_name=doc.name,
        )

    except Exception:
        # Do not block save due to notification errors
        frappe.log_error(
            frappe.get_traceback(),
            "Task: Notification Error in notify_assigned_contractor",
        )


def _get_contractor_email(employee_id: str) -> str | None:
    """
    Resolve an email for the given Employee.
    Priority: linked User.email -> Employee.company_email -> Employee.personal_email -> Employee.prefered_email

    Args:
        employee_id (str): Employee name/ID

    Returns:
        str | None: Email address or None if not found
    """
    if not employee_id:
        return None

    # Try linked User first
    user_id = frappe.db.get_value("Employee", employee_id, "user_id")
    if user_id:
        user_email = frappe.db.get_value("User", user_id, "email")
        if user_email:
            return user_email

    # Fallback to common email fields on Employee
    email_fields = [
        "company_email",
        "personal_email",
        "prefered_email",
        "prefered_contact_email",
    ]
    employee = frappe.db.get_value("Employee", employee_id, email_fields, as_dict=True)
    if employee:
        for f in email_fields:
            eml = employee.get(f)
            if eml:
                return eml

    return None
