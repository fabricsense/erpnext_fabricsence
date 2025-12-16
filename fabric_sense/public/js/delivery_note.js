// Child table event handler for Delivery Note Item
frappe.ui.form.on("Delivery Note Item", {
	item_code: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];

		// Only proceed if item_code is selected and sku field is empty
		if (row.item_code && !row.custom_sku) {
			// Fetch SKU from Item master
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Item",
					fieldname: "custom_sku",
					filters: {
						name: row.item_code,
					},
				},
				callback: function (r) {
					if (r.message && r.message.custom_sku) {
						// Set the SKU value in the child table row
						frappe.model.set_value(cdt, cdn, "custom_sku", r.message.custom_sku);
					}
				},
			});
		}
	},
});