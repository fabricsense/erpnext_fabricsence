import frappe


def force_item_price_name_to_code(doc, method: str | None = None) -> None:
    """Ensure Item Price.item_name always matches item_code.

    This runs on validate/before_save so that all Item Price records,
    regardless of how they are created (UI, import, API), store the
    full item_code in the item_name field for consistency.
    """
    if not getattr(doc, "item_code", None):
        return

    # Always mirror the code into item_name
    doc.item_name = doc.item_code


