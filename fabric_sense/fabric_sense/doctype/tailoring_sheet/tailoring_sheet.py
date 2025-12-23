import frappe  # type: ignore
from frappe import _  # type: ignore
from frappe.model.document import Document  # type: ignore


class TailoringSheet(Document):
    def validate(self):
        """Validate document before saving"""
        self.validate_project_uniqueness()

    def before_save(self):
        """Hook called before saving the document"""
        self.set_final_quantities()

    def validate_project_uniqueness(self):
        """Ensure only one Tailoring Sheet per Project"""
        if self.project:
            # Check for existing Tailoring Sheet with same project
            existing = frappe.db.exists(
                "Tailoring Sheet",
                {
                    "project": self.project,
                    "name": ["!=", self.name],  # Exclude current document
                    "docstatus": ["!=", 2]  # Exclude cancelled documents
                }
            )
            if existing:
                frappe.throw(
                    f"Tailoring Sheet '{existing}' already exists for Project '{self.project}'. "
                    "Only one Tailoring Sheet is allowed per Project.",
                    title="Duplicate Project"
                )

    def set_final_quantities(self):
        """Set final quantities from base quantities if empty or 0 in child table"""
        for row in self.measurement_details:
            # Set final fabric quantity if empty or 0
            if not row.final_fabric_quantity or row.final_fabric_quantity == 0:
                row.final_fabric_quantity = row.fabric_qty

            # Set final lining quantity if empty or 0
            if not row.final_lining_quantity or row.final_lining_quantity == 0:
                row.final_lining_quantity = row.lining_qty


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_available_measurement_sheets(
    doctype, txt, searchfield, start, page_len, filters
):
    """
    Query function to get measurement sheets that are:
    1. Approved status
    2. Not already selected in other tailoring sheets (except current one)
    """
    current_tailoring_sheet = filters.get("current_tailoring_sheet", "")

    # Get list of measurement sheets already used in other tailoring sheets
    used_measurement_sheets = frappe.db.sql(
        """
		SELECT DISTINCT measurement_sheet
		FROM `tabTailoring Sheet`
		WHERE measurement_sheet IS NOT NULL
		AND measurement_sheet != ''
		AND name != %(current_tailoring_sheet)s
		""",
        {"current_tailoring_sheet": current_tailoring_sheet},
        as_dict=False,
    )

    # Extract the measurement sheet names from the result
    used_ms_list = (
        [ms[0] for ms in used_measurement_sheets] if used_measurement_sheets else []
    )

    # Build the query to get available measurement sheets
    conditions = ["status = 'Approved'"]
    query_params = {}

    if txt:
        conditions.append("name LIKE %(txt)s")
        query_params["txt"] = f"%{txt}%"

    if used_ms_list:
        # Exclude already used measurement sheets using named parameters
        placeholders = ", ".join([f"%(ms_{i})s" for i in range(len(used_ms_list))])
        conditions.append(f"name NOT IN ({placeholders})")
        # Add each measurement sheet to query params
        for i, ms in enumerate(used_ms_list):
            query_params[f"ms_{i}"] = ms

    query = f"""
		SELECT name
		FROM `tabMeasurement Sheet`
		WHERE {' AND '.join(conditions)}
		ORDER BY modified DESC
	"""

    return frappe.db.sql(query, query_params)


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


@frappe.whitelist()
def get_remaining_quantities(tailoring_sheet):
    """
    Calculate remaining quantities for each item in the Tailoring Sheet
    by subtracting quantities already requested in Material Requests.
    Service items (parent item group is "Stitching" or "Labour") are excluded.
    """
    # Get the Tailoring Sheet document
    ts_doc = frappe.get_doc("Tailoring Sheet", tailoring_sheet)
    
    # Dictionary to store aggregated quantities by item
    item_quantities = {}
    
    # Aggregate quantities from measurement details
    for row in ts_doc.measurement_details:
        # Fabric Selected
        if row.fabric_selected and row.final_fabric_quantity:
            if row.fabric_selected not in item_quantities:
                item_quantities[row.fabric_selected] = {
                    "total_qty": 0,
                    "uom": "Meter"  # Default UOM for fabric
                }
            item_quantities[row.fabric_selected]["total_qty"] += row.final_fabric_quantity
        
        # Lining Selected
        if row.lining and row.final_lining_quantity:
            if row.lining not in item_quantities:
                item_quantities[row.lining] = {
                    "total_qty": 0,
                    "uom": "Meter"  # Default UOM for lining
                }
            item_quantities[row.lining]["total_qty"] += row.final_lining_quantity
        
        # Lead Rope Selected
        if row.lead_rope and row.lead_rope_qty:
            if row.lead_rope not in item_quantities:
                item_quantities[row.lead_rope] = {
                    "total_qty": 0,
                    "uom": "Meter"  # Default UOM for lead rope
                }
            item_quantities[row.lead_rope]["total_qty"] += row.lead_rope_qty
        
        # Hardware (Track/Rod)
        if row.track_rod and row.track_rod_qty:
            if row.track_rod not in item_quantities:
                item_quantities[row.track_rod] = {
                    "total_qty": 0,
                    "uom": "Foot"  # Default UOM for hardware
                }
            item_quantities[row.track_rod]["total_qty"] += row.track_rod_qty
    
    # Get quantities already requested in Material Requests
    requested_quantities = {}
    
    # Query all Material Requests linked to this Tailoring Sheet
    material_requests = frappe.get_all(
        "Material Request",
        filters={
            "custom_tailoring_sheet": tailoring_sheet,
            "docstatus": ["!=", 2]  # Exclude cancelled documents
        },
        fields=["name"]
    )
    
    # Get items from all Material Requests
    for mr in material_requests:
        mr_items = frappe.get_all(
            "Material Request Item",
            filters={"parent": mr.name},
            fields=["item_code", "qty"]
        )
        
        for item in mr_items:
            if item.item_code not in requested_quantities:
                requested_quantities[item.item_code] = 0
            requested_quantities[item.item_code] += item.qty
    
    # Calculate remaining quantities, excluding service items
    result_items = []
    for item_code, data in item_quantities.items():
        # Skip service items (parent item group is "Stitching" or "Labour")
        if is_service_item(item_code):
            continue
        
        total_qty = data["total_qty"]
        requested_qty = requested_quantities.get(item_code, 0)
        remaining_qty = total_qty - requested_qty
        
        result_items.append({
            "item_code": item_code,
            "total_qty": total_qty,
            "requested_qty": requested_qty,
            "remaining_qty": remaining_qty,
            "uom": data["uom"]
        })
    
    return {"items": result_items}


@frappe.whitelist()
def create_multi_material_request(tailoring_sheet):
    """
    Create two Material Requests from Tailoring Sheet:
    - Purchase type: for items with 'Is On Order Item' checked
    - Material Issue type: for all other items
    
    Args:
        tailoring_sheet (str): Tailoring Sheet name
        
    Returns:
        dict: Contains purchase_mr and issue_mr names
    """
    try:
        # Get the Tailoring Sheet document
        ts_doc = frappe.get_doc("Tailoring Sheet", tailoring_sheet)
        
        # Get remaining quantities (already excludes service items)
        remaining_data = get_remaining_quantities(tailoring_sheet)
        
        if not remaining_data or not remaining_data.get("items"):
            return {
                "purchase_mr": None,
                "issue_mr": None
            }
        
        # Separate items based on 'Is On Order Item' field
        purchase_items = []
        issue_items = []
        
        for item_data in remaining_data["items"]:
            # Only include items with remaining quantity > 0
            if item_data["remaining_qty"] <= 0:
                continue
            
            item_code = item_data["item_code"]
            
            # Check if item has 'Is On Order Item' checked
            is_on_order = frappe.db.get_value("Item", item_code, "custom_is_onorder_item")
            
            if is_on_order:
                purchase_items.append(item_data)
            else:
                issue_items.append(item_data)
        
        result = {
            "purchase_mr": None,
            "issue_mr": None
        }
        
        # Create Purchase Material Request if there are on-order items
        if purchase_items:
            purchase_mr = create_material_request_from_items(
                ts_doc, 
                purchase_items, 
                "Purchase"
            )
            if purchase_mr:
                result["purchase_mr"] = purchase_mr.name
        
        # Create Material Issue Request for other items
        if issue_items:
            issue_mr = create_material_request_from_items(
                ts_doc, 
                issue_items, 
                "Material Issue"
            )
            if issue_mr:
                result["issue_mr"] = issue_mr.name
        
        return result
        
    except Exception as e:
        frappe.log_error(
            f"Error creating multi material request for {tailoring_sheet}: {str(e)}\n{frappe.get_traceback()}",
            "Multi Material Request Error"
        )
        frappe.throw(_("Error creating Material Requests: {0}").format(str(e)))


def create_material_request_from_items(ts_doc, items, material_request_type):
    """
    Create a Material Request from given items.
    
    Args:
        ts_doc (Document): Tailoring Sheet document
        items (list): List of item dictionaries with item_code, remaining_qty, uom
        material_request_type (str): "Purchase" or "Material Issue"
        
    Returns:
        Document: Created Material Request document or None
    """
    if not items:
        return None
    
    try:
        # Get company from project or use default
        company = None
        if ts_doc.project:
            company = frappe.db.get_value("Project", ts_doc.project, "company")
        
        if not company:
            # Get default company
            company = frappe.db.get_single_value("Global Defaults", "default_company")
        
        # Check if there are existing Material Requests for this Tailoring Sheet
        existing_mrs = frappe.get_all(
            "Material Request",
            filters={
                "custom_tailoring_sheet": ts_doc.name,
                "docstatus": ["!=", 2]  # Exclude cancelled
            },
            fields=["name"]
        )
        
        # Create Material Request
        mr_doc = frappe.new_doc("Material Request")
        mr_doc.material_request_type = material_request_type
        mr_doc.transaction_date = frappe.utils.today()
        mr_doc.schedule_date = frappe.utils.add_days(frappe.utils.today(), 7)
        mr_doc.company = company
        mr_doc.custom_tailoring_sheet = ts_doc.name
        
        # Set approval status: if no existing MRs, it's first request (Approved)
        # If there are existing MRs, it's additional request (Pending)
        if not existing_mrs:
            mr_doc.custom_manager_approval_status = "Approved"
        # else:
        #     mr_doc.custom_manager_approval_status = "Pending"
        #     mr_doc.custom_is_additional = 1
        
        # Add items to Material Request
        for item_data in items:
            if item_data.get("remaining_qty", 0) > 0:
                mr_doc.append("items", {
                    "item_code": item_data["item_code"],
                    "qty": item_data["remaining_qty"],
                    "uom": item_data.get("uom", "Nos"),
                    "schedule_date": frappe.utils.add_days(frappe.utils.today(), 7)
                })
        
        mr_doc.insert()
        mr_doc.submit()
        
        frappe.db.commit()
        
        return mr_doc
        
    except Exception as e:
        frappe.log_error(
            f"Error creating {material_request_type} Material Request: {str(e)}\n{frappe.get_traceback()}",
            f"Create {material_request_type} MR Error"
        )
        return None
