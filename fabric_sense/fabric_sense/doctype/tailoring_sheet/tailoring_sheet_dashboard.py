from frappe import _  # type: ignore


def get_data():
    return {
        "fieldname": "custom_tailoring_sheet",
        "non_standard_fieldnames": {
            "Material Request": "custom_tailoring_sheet",
        },
        "internal_links": {
            "Material Request": ["custom_tailoring_sheet", "material_request"],
        },
        "transactions": [
            {
                "label": _("Material"),
                "items": ["Material Request"],
            }
        ],
    }
