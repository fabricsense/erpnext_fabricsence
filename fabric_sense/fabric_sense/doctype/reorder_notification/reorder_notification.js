// Copyright (c) 2025, innogenio and contributors
// For license information, please see license.txt

frappe.ui.form.on("Reorder Notification", {
	refresh(frm) {
		// Add custom buttons for actions
		if (frm.doc.status === "Pending") {
			frm.add_custom_button(__("Mark as Read"), function() {
				frappe.call({
					method: "fabric_sense.fabric_sense.py.reorder_monitoring.mark_reorder_notification_as_read",
					args: {
						notification_name: frm.doc.name
					},
					callback: function(r) {
						if (!r.exc) {
							frm.reload_doc();
						}
					}
				});
			});
		}

		// Show current stock balance
		if (frm.doc.item && frm.doc.warehouse) {
			frappe.call({
				method: "erpnext.stock.utils.get_stock_balance",
				args: {
					item_code: frm.doc.item,
					warehouse: frm.doc.warehouse
				},
				callback: function(r) {
					if (r.message !== undefined) {
						frm.dashboard.add_indicator(__("Current Stock: {0}", [r.message]), "blue");
					}
				}
			});
		}

		// Set color indicator based on status
		if (frm.doc.status === "Pending") {
			frm.dashboard.set_headline_alert(
				__("Reorder Required: Stock below minimum level"),
				"red"
			);
		} else if (frm.doc.status === "Readed") {
			frm.dashboard.set_headline_alert(
				__("Notification has been acknowledged"),
				"green"
			);
		}
	},

	item: function(frm) {
		// Update item name when item is selected
		if (frm.doc.item) {
			frappe.db.get_value("Item", frm.doc.item, "item_name", function(r) {
				if (r && r.item_name) {
					frm.set_df_property("item", "description", r.item_name);
				}
			});
		}
	},

});
