frappe.ui.form.on("Item", {
	refresh: function (frm) {
		// Update preferred vendor options on form load
		update_preferred_vendor_options(frm);
	},

	custom_vendor_code_selection: function (frm) {
		// Update preferred vendor options when vendor selection changes
		update_preferred_vendor_options(frm);
	},

	custom_discounted: function (frm) {
		// Clear discount value when Discounted checkbox is unchecked
		if (!frm.doc.custom_discounted && frm.doc.custom_discount_value) {
			frm.set_value("custom_discount_value", null);
		}
	},

	custom_is_onorder_item: function (frm) {
		// Clear dependent fields when "Is On Order Item" is unchecked
		if (!frm.doc.custom_is_onorder_item) {
			const fields_to_clear = [
				"custom_shade_number",
				"custom_serial_number",
				"custom_catalogue_name",
			];
			fields_to_clear.forEach((field) => {
				if (frm.doc[field]) {
					frm.set_value(field, null);
				}
			});
		}
	},
});

frappe.ui.form.on("Vender Selection", {
	vendor: function (frm, cdt, cdn) {
		// Update preferred vendor options when a vendor is added/changed in the child table
		update_preferred_vendor_options(frm);
	},

	vender_selection_remove: function (frm, cdt, cdn) {
		// Update preferred vendor options when a vendor is removed from the child table
		update_preferred_vendor_options(frm);
	},
});

function update_preferred_vendor_options(frm) {
	// Get all selected vendors from the child table
	let selected_vendors = [];

	if (frm.doc.custom_vendor_code_selection) {
		selected_vendors = frm.doc.custom_vendor_code_selection
			.map((row) => row.vendor)
			.filter((v) => v);
	}

	console.log("Selected vendors:", selected_vendors);

	if (selected_vendors.length === 0) {
		// Clear the preferred vendor field if no vendors are selected
		frm.set_df_property("custom_vendor_code", "options", "");
		frm.refresh_field("custom_vendor_code");
		return;
	}

	// Fetch vendor codes for the selected vendors
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Supplier",
			filters: {
				name: ["in", selected_vendors],
			},
			fields: ["name", "custom_vendor_code"],
		},
		callback: function (r) {
			console.log("Supplier data received:", r.message);

			if (r.message) {
				// Build options for the preferred vendor dropdown
				let options = [];

				r.message.forEach((supplier) => {
					// Only include suppliers that have a vendor code
					if (supplier.custom_vendor_code) {
						options.push(supplier.custom_vendor_code + " - " + supplier.name);
					}
				});

				console.log("Generated options:", options);

				// Set the options for the preferred vendor field
				if (options.length > 0) {
					frm.set_df_property("custom_vendor_code", "options", options.join("\n"));
				} else {
					// Show "No Data Found" if no vendor codes exist
					frm.set_df_property("custom_vendor_code", "options", "");
				}

				frm.refresh_field("custom_vendor_code");

				// Clear the preferred vendor value if it's not in the new options
				if (frm.doc.custom_vendor_code) {
					let current_value = frm.doc.custom_vendor_code;
					if (!options.includes(current_value) && current_value !== "No Data Found") {
						frm.set_value("custom_vendor_code", "");
					}
				}
			}
		},
	});
}
