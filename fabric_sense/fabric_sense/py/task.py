import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime


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
                uom_field_names = [
                    "custom_unit",
                    "unit",
                    "custom_uom",
                    "uom"
                ]
                for field_name in uom_field_names:
                    if hasattr(doc, field_name) and not doc.get(field_name):
                        setattr(doc, field_name, services_doc.uom)
                        break
        except Exception as e:
            frappe.log_error(
                message=f"Error pre-filling UOM: {str(e)}",
                title="Task: UOM Prefill Error"
            )

    # 3) Prefill service rate & charges if data exists
    has_service = hasattr(doc, "custom_service") and doc.custom_service
    has_contractor = hasattr(doc, "custom_assigned_contractor") and doc.custom_assigned_contractor
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
    if hasattr(doc, 'custom_tailoring_sheet') and doc.custom_tailoring_sheet:
        tailoring_sheet = doc.custom_tailoring_sheet
    elif hasattr(doc, 'tailoring_sheet') and doc.tailoring_sheet:
        tailoring_sheet = doc.tailoring_sheet
    
    if not tailoring_sheet:
        frappe.throw(_("Please select a Tailoring Sheet before changing status to Working. Material Request and Stock Entry cannot be created without a Tailoring Sheet."))
    
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
    
    if hasattr(doc, 'custom_service') and doc.custom_service and \
       hasattr(doc, 'custom_assigned_contractor') and doc.custom_assigned_contractor:
        # Get service rate for the selected contractor and service
        service_rate = get_service_rate(
            service=doc.custom_service,
            contractor=doc.custom_assigned_contractor
        )
        
        # 3. Calculate Service Charge = Service Rate × Quantity
        quantity = (hasattr(doc, 'custom_quantity') and doc.custom_quantity) or 1.0
        service_charge = service_rate * quantity
        
        # 4. Calculate Total Contractor Amount = Service Charge + Travelling Charge
        travelling_charge = (hasattr(doc, 'custom_travelling_charge') and doc.custom_travelling_charge) or 0.0
        total_contractor_amount = service_charge + travelling_charge
    
    # 5. Write results to Task fields
    if hasattr(doc, 'custom_service_rate'):
        doc.custom_service_rate = service_rate
    if hasattr(doc, 'custom_service_charge'):
        doc.custom_service_charge = service_charge
    if hasattr(doc, 'custom_total_contractor_amount'):
        doc.custom_total_contractor_amount = total_contractor_amount


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
                alert=True
            )
        return 0.0
        
    except frappe.DoesNotExistError:
        if show_message:
            frappe.msgprint(
                _("Service {0} not found").format(service),
                indicator="orange",
                alert=True
            )
        return 0.0
    except Exception as e:
        frappe.log_error(
            message=f"Error fetching service rate: {str(e)}",
            title="Task: Service Rate Error"
        )
        return 0.0


@frappe.whitelist()
def get_service_rate_and_calculate_charges(service, contractor, quantity=1.0, travelling_charge=0.0):
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
            if hasattr(services_doc, 'uom') and services_doc.uom:
                uom = services_doc.uom
        except Exception as e:
            frappe.log_error(
                message=f"Error fetching UOM from Services: {str(e)}",
                title="Task: UOM Fetch Error"
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
        "uom": uom
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
                if hasattr(item_group_doc, 'parent_item_group') and item_group_doc.parent_item_group:
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
        if not hasattr(tailoring_sheet, 'measurement_details') or not tailoring_sheet.measurement_details:
            frappe.throw(_("Tailoring Sheet has no items to create Material Request. Please add items in measurement_details."))
        
        # Extract items from measurement_details
        for row in tailoring_sheet.measurement_details:
            # Fabric Selected
            if row.fabric_selected and row.final_fabric_quantity and row.final_fabric_quantity > 0:
                if row.fabric_selected not in item_quantities:
                    item_quantities[row.fabric_selected] = 0.0
                item_quantities[row.fabric_selected] += float(row.final_fabric_quantity)
            
            # Lining
            if row.lining and row.final_lining_quantity and row.final_lining_quantity > 0:
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
                items.append({
                    "item_code": item_code,
                    "qty": qty
                })
        
        # Validate that we have at least one item
        if not items:
            frappe.throw(_("Tailoring Sheet has no items to create Material Request. Please ensure measurement_details contains items with quantities."))
        
        return items
        
    except frappe.DoesNotExistError:
        frappe.throw(_("Tailoring Sheet {0} not found").format(tailoring_sheet_name))
    except Exception as e:
        frappe.log_error(
            message=f"Error extracting items from Tailoring Sheet: {str(e)}",
            title="Task: Extract Items Error"
        )
        frappe.throw(_("Error extracting items from Tailoring Sheet: {0}").format(str(e)))


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
                "docstatus": ["!=", 2]  # Not cancelled
            },
            ["name", "docstatus"],
            as_dict=True
        )
        
        # If Material Request exists
        if material_request:
            # Check if it's submitted
            if material_request.docstatus == 1:
                # Material Request is submitted, return it
                mr_doc = frappe.get_doc("Material Request", material_request.name)
                items = []
                
                for item in mr_doc.items:
                    items.append({
                        "item_code": item.item_code,
                        "qty": item.qty,
                        "uom": item.uom,
                        "item_name": item.item_name,
                        "description": item.description,
                        "name": item.name  # Row name for linking
                    })
                
                return {
                    "material_request_name": material_request.name,
                    "items": items,
                    "created": False
                }
            else:
                # Material Request exists but is not submitted
                frappe.throw(
                    _("Material Request {0} exists but is not submitted. Please submit it before continuing.").format(
                        material_request.name
                    )
                )
        
        # Material Request does not exist, create it
        # Extract items from Tailoring Sheet
        items = extract_items_from_tailoring_sheet(tailoring_sheet)
        
        # Create Material Request
        mr_doc = frappe.get_doc({
            "doctype": "Material Request",
            "material_request_type": "Material Issue",
            "custom_tailoring_sheet": tailoring_sheet,
            "transaction_date": frappe.utils.today(),
            "schedule_date": frappe.utils.today()
        })
        
        # Add items to Material Request
        for item in items:
            # Get item details for UOM
            item_doc = frappe.get_doc("Item", item["item_code"])
            default_uom = item_doc.stock_uom if hasattr(item_doc, 'stock_uom') and item_doc.stock_uom else "Nos"
            
            mr_doc.append("items", {
                "item_code": item["item_code"],
                "qty": item["qty"],
                "uom": default_uom,
                "schedule_date": frappe.utils.today()
            })
        
        # Save Material Request
        mr_doc.insert()
        
        # Submit Material Request automatically
        mr_doc.submit()
        
        # Prepare items list for return
        items_list = []
        for item in mr_doc.items:
            items_list.append({
                "item_code": item.item_code,
                "qty": item.qty,
                "uom": item.uom,
                "item_name": item.item_name,
                "description": item.description,
                "name": item.name  # Row name for linking
            })
        
        return {
            "material_request_name": mr_doc.name,
            "items": items_list,
            "created": True
        }
        
    except frappe.ValidationError:
        # Re-raise validation errors
        raise
    except Exception as e:
        frappe.log_error(
            message=f"Error in get_or_create_material_request_for_task: {str(e)}",
            title="Task: MR Creation Error"
        )
        frappe.throw(_("Error creating Material Request: {0}").format(str(e)))


@frappe.whitelist()
def get_material_request_items_for_stock_entry(tailoring_sheet):
    """
    Get Material Request items for Stock Entry creation.
    
    Finds Material Request with type "Material Issue" linked to the Tailoring Sheet via custom_tailoring_sheet.
    Checks for submitted Material Request first, then draft if not found.
    
    Args:
        tailoring_sheet (str): Tailoring Sheet name
        
    Returns:
        dict: Contains material_request_name, items list, docstatus, and message
    """
    try:
        # First, try to find submitted Material Request with type "Material Issue" linked to Tailoring Sheet
        material_request = frappe.db.get_value(
            "Material Request",
            {
                "custom_tailoring_sheet": tailoring_sheet,
                "material_request_type": "Material Issue",
                "docstatus": 1  # Submitted
            },
            ["name", "docstatus"],
            as_dict=True,
            order_by="creation desc"
        )
        
        # If no submitted MR found, check for draft MR
        if not material_request:
            material_request = frappe.db.get_value(
                "Material Request",
                {
                    "custom_tailoring_sheet": tailoring_sheet,
                    "material_request_type": "Material Issue",
                    "docstatus": 0  # Draft
                },
                ["name", "docstatus"],
                as_dict=True,
                order_by="creation desc"
            )
        
        if not material_request:
            return {
                "material_request_name": None,
                "items": [],
                "docstatus": None,
                "message": "No Material Request (Material Issue) found for this Tailoring Sheet"
            }
        
        # Get Material Request items
        mr_doc = frappe.get_doc("Material Request", material_request.name)
        items = []
        
        for item in mr_doc.items:
            # Get stock_uom from Item master
            stock_uom = None
            try:
                item_doc = frappe.get_doc("Item", item.item_code)
                stock_uom = item_doc.stock_uom if hasattr(item_doc, 'stock_uom') and item_doc.stock_uom else item.uom
            except Exception:
                # If item not found or error, use uom from Material Request as fallback
                stock_uom = item.uom
            
            items.append({
                "item_code": item.item_code,
                "qty": item.qty,
                "uom": item.uom,
                "stock_uom": stock_uom,
                "item_name": item.item_name,
                "description": item.description,
                "name": item.name  # Row name for linking
            })
        
        return {
            "material_request_name": material_request.name,
            "items": items,
            "docstatus": material_request.docstatus,
            "message": None if material_request.docstatus == 1 else "Material Request is not submitted. Please submit it before creating Stock Entry."
        }
        
    except Exception as e:
        frappe.log_error(
            message=f"Error fetching Material Request items: {str(e)}",
            title="Task: MR Items Fetch Error"
        )
        return {
            "material_request_name": None,
            "items": [],
            "error": str(e)
        }


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
        if hasattr(services_doc, 'contractors') and services_doc.contractors:
            for contractor_row in services_doc.contractors:
                if contractor_row.contractor:
                    contractors.append(contractor_row.contractor)
        
        return contractors
        
    except frappe.DoesNotExistError:
        return []
    except Exception as e:
        frappe.log_error(
            message=f"Error fetching contractors for service: {str(e)}",
            title="Task: Get Contractors Error"
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
            "Tailoring Sheet",
            {"project": project},
            "name",
            order_by="creation desc"
        )
        
        return tailoring_sheet
        
    except Exception as e:
        frappe.log_error(
            message=f"Error fetching latest tailoring sheet for project: {str(e)}",
            title="Task: Get Latest Tailoring Sheet Error"
        )
        return None
