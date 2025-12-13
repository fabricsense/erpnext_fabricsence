from frappe import _  # type: ignore


def get_data():
    return {
        "fieldname": "measurement_sheet",
        "non_standard_fieldnames": {
            "Tailoring Sheet": "measurement_sheet",
        },
        # "internal_links": {
        #     "Tailoring Sheet": ["measurement_sheet", "measurement_sheet"],
        # },
        "transactions": [
            {
                "label": _("Tailoring Sheet"),
                "items": ["Tailoring Sheet"],
            }
        ],
    }
