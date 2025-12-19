frappe.ui.form.on("Item", {
	refresh: function (frm) {
		// Update preferred vendor options on form load
		update_preferred_vendor_options(frm);
		
		// Check if item group exists in any brand and show/hide brand field accordingly
		toggle_brand_field_visibility(frm);
		
		// Set up brands filter based on item group
		setup_brands_filter(frm);
		
		// Update catalogue options based on selected brand (preserve existing value on refresh)
		update_catalogue_options(frm, true);
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

	item_group: function (frm) {
		// Auto-fill category code when Item Group is selected
		if (frm.doc.item_group) {
			console.log("Item Group selected:", frm.doc.item_group);

			// Fetch Item Group to get the category code
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Item Group",
					name: frm.doc.item_group,
				},
				callback: function (r) {
					if (r.message && r.message.custom_category_code) {
						console.log("Category Code from Item Group:", r.message.custom_category_code);
						frm.set_value("custom_category_code", r.message.custom_category_code);
					} else {
						console.log("No category code found in Item Group");
						// Clear category code if Item Group has no category code
						frm.set_value("custom_category_code", null);
					}
				},
			});
		} else {
			// Clear the category code field if Item Group is cleared
			frm.set_value("custom_category_code", null);
		}
		
		// Check if item group exists in any brand and show/hide brand field accordingly
		toggle_brand_field_visibility(frm);
		
		// Update brands filter and clear brands field when item group changes
		setup_brands_filter(frm);
		if (!frm.doc.item_group) {
			frm.set_value("custom_brands", null);
		}
	},

	custom_brands: function (frm) {
		// Update catalogue options when brand is selected
		update_catalogue_options(frm);
	},

	gst_hsn_code: function (frm) {
		// Auto-fill custom_hsn_code and custom_gst_rate when HSN/SAC is selected
		if (frm.doc.gst_hsn_code) {
			console.log("HSN/SAC selected:", frm.doc.gst_hsn_code);

			// Set the custom_hsn_code field with the selected HSN code
			frm.set_value("custom_hsn_code", frm.doc.gst_hsn_code);

			// Fetch GST HSN Code to get the linked Item Tax Template
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "GST HSN Code",
					name: frm.doc.gst_hsn_code,
				},
				callback: function (r) {
					if (r.message) {
						console.log("GST HSN Code data:", r.message);

						// Get the Item Tax Template from the HSN Code's taxes child table
						if (r.message.taxes && r.message.taxes.length > 0) {
							let item_tax_template = r.message.taxes[0].item_tax_template;
							console.log("Item Tax Template from HSN Code:", item_tax_template);

							if (item_tax_template) {
								// Fetch the actual GST rate from the Item Tax Template
								fetch_gst_rate_from_template(frm, item_tax_template);
							}
						} else {
							console.log("No taxes found in GST HSN Code");
						}
					}
				},
			});
		} else {
			// Clear the fields if HSN code is cleared
			frm.set_value("custom_hsn_code", null);
			frm.set_value("custom_gst_rate", null);
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

// Event handler for Item Tax child table
frappe.ui.form.on("Item Tax", {
	item_tax_template: function (frm, cdt, cdn) {
		// When Item Tax Template is changed, update the custom_gst_rate
		let row = locals[cdt][cdn];
		if (row.item_tax_template) {
			fetch_gst_rate_from_template(frm, row.item_tax_template);
		}
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

function fetch_gst_rate_from_template(frm, item_tax_template) {
	// Fetch GST rate from Item Tax Template
	console.log("Fetching GST rate from Item Tax Template:", item_tax_template);

	frappe.call({
		method: "frappe.client.get",
		args: {
			doctype: "Item Tax Template",
			name: item_tax_template,
		},
		callback: function (r) {
			console.log("Item Tax Template data:", r.message);

			if (r.message) {
				// Use the gst_rate field directly from Item Tax Template
				if (r.message.gst_rate !== undefined && r.message.gst_rate !== null) {
					console.log("GST Rate from Item Tax Template:", r.message.gst_rate);
					frm.set_value("custom_gst_rate", r.message.gst_rate);
				} else {
					console.log("No gst_rate field found in Item Tax Template");
				}
			}
		},
	});
}

function setup_brands_filter(frm) {
	// Set up filter for brands field based on selected item group
	if (frm.doc.item_group) {
		console.log("Setting up brands filter for item group:", frm.doc.item_group);
		
		frm.set_query("custom_brands", function() {
			return {
				query: "fabric_sense.fabric_sense.doctype.brands.brands.get_brands_by_item_group",
				filters: {
					item_group: frm.doc.item_group
				}
			};
		});
	} else {
		// Clear the filter if no item group is selected
		frm.set_query("custom_brands", function() {
			return {};
		});
	}
}

function update_catalogue_options(frm, preserve_value = false) {
	// Update catalogue field options based on selected brand
	if (frm.doc.custom_brands) {
		console.log("Brand selected:", frm.doc.custom_brands);
		
		// Fetch catalogues from the selected brand
		frappe.call({
			method: "fabric_sense.fabric_sense.doctype.brands.brands.get_catalogues_by_brand",
			args: {
				brand: frm.doc.custom_brands
			},
			callback: function (r) {
				console.log("Catalogues received:", r.message);
				
				if (r.message && r.message.length > 0) {
					// Set the options for the catalogue field
					let options = r.message.join("\n");
					frm.set_df_property("custom_catalogue", "options", options);
					
					// Only clear the catalogue value if this is a brand change (not form refresh)
					// and the current value is not in the new options
					if (!preserve_value && frm.doc.custom_catalogue) {
						if (!r.message.includes(frm.doc.custom_catalogue)) {
							frm.set_value("custom_catalogue", "");
						}
					}
				} else {
					// Clear options if no catalogues found
					frm.set_df_property("custom_catalogue", "options", "");
					// Only clear value if not preserving (i.e., during brand change)
					if (!preserve_value && frm.doc.custom_catalogue) {
						frm.set_value("custom_catalogue", "");
					}
				}
				
				frm.refresh_field("custom_catalogue");
			}
		});
	} else {
		// Clear catalogue options and value if no brand is selected
		frm.set_df_property("custom_catalogue", "options", "");
		frm.refresh_field("custom_catalogue");
		// Only clear value if not preserving (i.e., during brand change)
		if (!preserve_value && frm.doc.custom_catalogue) {
			frm.set_value("custom_catalogue", "");
		}
	}
}

function toggle_brand_field_visibility(frm) {
	// Show/hide brand field based on whether item group exists in any brand
	if (frm.doc.item_group) {
		console.log("Checking if item group exists in any brand:", frm.doc.item_group);
		
		// Check if the item group exists in any brand's sub-categories
		frappe.call({
			method: "fabric_sense.fabric_sense.doctype.brands.brands.check_item_group_in_brands",
			args: {
				item_group: frm.doc.item_group
			},
			callback: function (r) {
				console.log("Item group exists in brands:", r.message);
				
				if (r.message) {
					// Show brand field if item group exists in any brand
					frm.set_df_property("custom_brands", "hidden", 0);
					frm.set_df_property("custom_catalogue", "hidden", 0);
				} else {
					// Hide brand field and clear its value if item group doesn't exist in any brand
					frm.set_df_property("custom_brands", "hidden", 1);
					frm.set_df_property("custom_catalogue", "hidden", 1);
					if (frm.doc.custom_brands) {
						frm.set_value("custom_brands", null);
					}
					if (frm.doc.custom_catalogue) {
						frm.set_value("custom_catalogue", null);
					}
				}
				frm.refresh_field("custom_brands");
				frm.refresh_field("custom_catalogue");
			}
		});
	} else {
		// Hide brand field if no item group is selected
		frm.set_df_property("custom_brands", "hidden", 1);
		frm.set_df_property("custom_catalogue", "hidden", 1);
		frm.refresh_field("custom_brands");
		frm.refresh_field("custom_catalogue");
	}
}
