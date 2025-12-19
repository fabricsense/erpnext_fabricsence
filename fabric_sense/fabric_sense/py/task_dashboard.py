from frappe import _  # type: ignore


def get_data(data):
    """
    Override Task dashboard to add Stock Entry connections.
    
    Args:
        data: Base dashboard data from ERPNext
    
    Returns:
        Modified dashboard data with Stock Entry connections
    """
    # Add Stock Entry connections using custom_task field
    data["non_standard_fieldnames"] = data.get("non_standard_fieldnames", {})
    data["non_standard_fieldnames"]["Stock Entry"] = "custom_task"
    
    # Add internal links for Stock Entry
    data["internal_links"] = data.get("internal_links", {})
    data["internal_links"]["Stock Entry"] = ["custom_task", "custom_task"]
    
    # Add Stock Entry to transactions
    data["transactions"] = data.get("transactions", [])
    
    # Check if Stock section already exists
    stock_section_exists = False
    for section in data["transactions"]:
        if section.get("label") == _("Stock"):
            if "Stock Entry" not in section["items"]:
                section["items"].append("Stock Entry")
            stock_section_exists = True
            break
    
    # If Stock section doesn't exist, create it
    if not stock_section_exists:
        data["transactions"].append({
            "label": _("Stock"),
            "items": ["Stock Entry"],
        })
    
    return data