from __future__ import unicode_literals
import frappe  # type: ignore
from frappe.model.document import Document  # type: ignore
from frappe import _  # type: ignore


class Pattern(Document):
    def validate(self):
        if self.is_item and not self.item:
            self.create_item_and_link()

    def create_item_and_link(self):
        # Create Item
        item = frappe.new_doc("Item")
        item.item_code = self.pattern_name
        item.item_name = self.pattern_name
        item.item_group = self.item_group
        item.stock_uom = self.default_unit_of_measure
        item.gst_hsn_code = self.hsnsac
        item.custom_base_rate = 0.00
        item.is_stock_item = 0
        # item.include_item_in_manufacturing = 0
        item.save(ignore_permissions=True)

        # Get Standard Selling Price List
        price_list_name = frappe.db.get_value(
            "Price List", {"price_list_name": "Standard Selling", "enabled": 1}, "name"
        )

        if not price_list_name:
            frappe.throw(_("Standard Selling price list not found or disabled"))

        # Create Item Price
        item_price = frappe.new_doc("Item Price")
        item_price.item_code = item.name
        item_price.uom = self.default_unit_of_measure
        item_price.price_list = price_list_name
        item_price.price_list_rate = self.base_rate
        item_price.save(ignore_permissions=True)

        # Link Item to Pattern
        self.item = item.name
