// Copyright (c) 2025, innogenio and contributors
// For license information, please see license.txt

frappe.listview_settings["Reorder Notification"] = {
	onload: function (listview) {
		// Hide the default 'Add' button
		this.hide_add_button(listview);
	},
	add_fields: ["status", "current_quantity", "reorder_level"],

	get_indicator: function (doc) {
		if (doc.status === "Pending") {
			return [__("Pending"), "red", "status,=,Pending"];
		} else if (doc.status === "Readed") {
			return [__("Read"), "green", "status,=,Readed"];
		}
	},

	formatters: {
		current_quantity: function (value, field, doc) {
			if (parseFloat(value) < parseFloat(doc.reorder_level)) {
				return `<span style="color: red; font-weight: bold;">${value}</span>`;
			}
			return value;
		},

		reorder_level: function (value, field, doc) {
			return `<span style="color: orange; font-weight: bold;">${value}</span>`;
		},
	},
	hide_add_button: function (listview) {
		// Remove the default 'Add' button
		listview.page.clear_primary_action();

		// Hide the button using CSS if it still appears
		setTimeout(() => {
			$(".page-head").find('[data-label="Add%20Reorder%20Notification"]').hide();
			$(".page-head").find('button:contains("Add Contractor Payment History")').hide();
			$(".primary-action").hide();
		}, 100);
	},

	primary_action: function () {
		// Do nothing to suppress the default 'Add' button behavior
		return false;
	},
};
