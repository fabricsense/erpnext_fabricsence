from frappe import _ # type: ignore


def get_data(data):
    """
    Override Sales Order dashboard to use custom_sales_order field 
    for Material Request connections instead of the standard sales_order field.
    
    Args:
        data: Base dashboard data from ERPNext
    
    Returns:
        Modified dashboard data with custom field mapping
    """
    # Override only the Material Request connection to use custom_sales_order field
    data["non_standard_fieldnames"] = data.get("non_standard_fieldnames", {})
    data["non_standard_fieldnames"]["Material Request"] = "custom_sales_order"
    
    return data
