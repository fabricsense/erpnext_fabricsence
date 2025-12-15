from frappe import _  # type: ignore


def get_data(data):
    # Set the fieldname for customer
    data["fieldname"] = "customer"

    # Preserve existing non_standard_fieldnames and add new ones if they don't exist
    if "non_standard_fieldnames" not in data:
        data["non_standard_fieldnames"] = {}

    # Add or update the fieldnames for Measurement Sheet
    data["non_standard_fieldnames"].update(
        {
            "Measurement Sheet": "customer",
        }
    )

    # Preserve existing internal_links and add new ones if they don't exist
    # if "internal_links" not in data:
    #     data["internal_links"] = {}

    # # Add or update the internal links
    # data["internal_links"].update(
    #     {
    #         "Measurement Sheet": ["customer", "customer"],
    #     }
    # )

    # Initialize transactions if it doesn't exist
    if "transactions" not in data:
        data["transactions"] = []

    # Check if Fabric Sense section already exists
    fabric_sense_section = next(
        (t for t in data["transactions"] if t.get("label") == _("Fabric Sense")), None
    )

    if fabric_sense_section:
        # Update existing Fabric Sense section
        existing_items = set(fabric_sense_section.get("items", []))
        fabric_sense_section["items"] = list(
            existing_items.union({"Measurement Sheet"})
        )
    else:
        # Add new Fabric Sense section if it doesn't exist
        data["transactions"].append(
            {
                "label": _("Fabric Sense"),
                "items": ["Measurement Sheet"],
            }
        )

    return data
