frappe.provide("fabric_sense.tailoring_sheet");

fabric_sense.tailoring_sheet.setup_tailoring_sheet_form = function (frm) {
	// Set filter for Measurement Sheet field to show only Approved records
	// and exclude already selected measurement sheets in other tailoring sheets
	frm.set_query("measurement_sheet", function () {
		return {
			query: "fabric_sense.fabric_sense.doctype.tailoring_sheet.tailoring_sheet.get_available_measurement_sheets",
			filters: {
				current_tailoring_sheet: frm.doc.name || "",
			},
		};
	});

	// Hide the "Add Row" button for measurement_details child table
	frm.fields_dict["measurement_details"].grid.cannot_add_rows = true;
	frm.refresh_field("measurement_details");

	const pageActions = frm.page.page_actions;
	pageActions.find(".btn-primary").each(function () {
		const btnText = $(this).text().trim();
		if (btnText === "Create Material Request") {
			$(this).remove();
		}
	});

	// Add "Create Material Request" button when status is "Completed"
	if (frm.doc.status === "Completed" && !frm.is_new()) {
		frm.add_custom_button(__("Create Material Request"), function () {
			fabric_sense.tailoring_sheet.create_material_request(frm);
		})
			.addClass("btn-primary")
			.prependTo(frm.page.page_actions);
	}
};

fabric_sense.tailoring_sheet.handle_measurement_sheet_change = function (frm) {
	// Fetch data from Measurement Sheet when selected
	if (frm.doc.measurement_sheet) {
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Measurement Sheet",
				name: frm.doc.measurement_sheet,
			},
			callback: function (r) {
				if (r.message) {
					// Set the fetched values
					frm.set_value("customer", r.message.customer);
					frm.set_value("project", r.message.project);
					frm.set_value("tailor_assigned", r.message.assigned_contractor);

					// Clear existing measurement details
					frm.clear_table("measurement_details");

					// Copy measurement details from Measurement Sheet
					if (
						r.message.measurement_details &&
						r.message.measurement_details.length > 0
					) {
						r.message.measurement_details.forEach(function (row) {
							let child = frm.add_child("measurement_details");
							// Copy all fields from the source row to the child row
							for (let key in row) {
								if (
									key !== "name" &&
									key !== "owner" &&
									key !== "creation" &&
									key !== "modified" &&
									key !== "modified_by" &&
									key !== "parent" &&
									key !== "parentfield" &&
									key !== "parenttype" &&
									key !== "doctype" &&
									key !== "idx"
								) {
									child[key] = row[key];
								}
							}
						});
						frm.refresh_field("measurement_details");
					}
				}
			},
		});
	} else {
		// Clear fields if measurement sheet is cleared
		frm.set_value("customer", "");
		frm.set_value("project", "");
		frm.set_value("tailor_assigned", "");
		frm.clear_table("measurement_details");
		frm.refresh_field("measurement_details");
	}
};

// Helper functions for Tailoring Measurement Details calculations
fabric_sense.tailoring_sheet.calculate_fabric_adjust = function (cdt, cdn) {
	// Validate that fabric_adjust is not negative
	let row = locals[cdt][cdn];

	if (row.fabric_adjust !== undefined && row.fabric_adjust < 0) {
		frappe.show_alert(
			{
				message: __("Fabric Adjust cannot be negative"),
				indicator: "red",
			},
			5
		);
		// Reset the value to 0
		frappe.model.set_value(cdt, cdn, "fabric_adjust", 0);
		return;
	}

	// Auto-calculate final fabric quantity when fabric adjust is entered
	if (row.fabric_qty !== undefined && row.fabric_adjust !== undefined) {
		frappe.model.set_value(
			cdt,
			cdn,
			"final_fabric_quantity",
			(row.fabric_qty || 0) + (row.fabric_adjust || 0)
		);
	}
};

fabric_sense.tailoring_sheet.calculate_lining_adjust = function (cdt, cdn) {
	// Validate that lining_adjust is not negative
	let row = locals[cdt][cdn];

	if (row.lining_adjust !== undefined && row.lining_adjust < 0) {
		frappe.show_alert(
			{
				message: __("Lining Adjust cannot be negative"),
				indicator: "red",
			},
			5
		);
		// Reset the value to 0
		frappe.model.set_value(cdt, cdn, "lining_adjust", 0);
		return;
	}

	// Auto-calculate final lining quantity when lining adjust is entered
	if (row.lining_qty !== undefined && row.lining_adjust !== undefined) {
		frappe.model.set_value(
			cdt,
			cdn,
			"final_lining_quantity",
			(row.lining_qty || 0) + (row.lining_adjust || 0)
		);
	}
};

fabric_sense.tailoring_sheet.calculate_final_fabric_quantity = function (cdt, cdn) {
	// Auto-calculate fabric amount when final fabric quantity changes
	let row = locals[cdt][cdn];
	if (row.final_fabric_quantity !== undefined && row.fabric_rate !== undefined) {
		frappe.model.set_value(
			cdt,
			cdn,
			"fabric_amount",
			(row.final_fabric_quantity || 0) * (row.fabric_rate || 0)
		);
	}
};

fabric_sense.tailoring_sheet.calculate_final_lining_quantity = function (cdt, cdn) {
	// Auto-calculate lining amount when final lining quantity changes
	let row = locals[cdt][cdn];
	if (row.final_lining_quantity !== undefined && row.lining_rate !== undefined) {
		frappe.model.set_value(
			cdt,
			cdn,
			"lining_amount",
			(row.final_lining_quantity || 0) * (row.lining_rate || 0)
		);
	}
};

fabric_sense.tailoring_sheet.calculate_fabric_amount = function (cdt, cdn) {
	// Auto-calculate total amount when fabric amount changes
	let row = locals[cdt][cdn];
	let total =
		(row.fabric_amount || 0) +
		(row.lining_amount || 0) +
		(row.lead_rope_amount || 0) +
		(row.track_rod_amount || 0) +
		(row.stitching_charge || 0) +
		(row.fitting_charge || 0);
	frappe.model.set_value(cdt, cdn, "amount", total);
};

fabric_sense.tailoring_sheet.calculate_lining_amount = function (cdt, cdn) {
	// Auto-calculate total amount when lining amount changes
	let row = locals[cdt][cdn];
	let total =
		(row.fabric_amount || 0) +
		(row.lining_amount || 0) +
		(row.lead_rope_amount || 0) +
		(row.track_rod_amount || 0);
	frappe.model.set_value(cdt, cdn, "amount", total);
};

fabric_sense.tailoring_sheet.create_material_request = function (frm) {
	// Call server method to get remaining quantities and create Material Request
	// Note: Service items (parent item group is "Stitching" or "Labour") are already
	// filtered out by the server-side get_remaining_quantities method
	frappe.call({
		method: "fabric_sense.fabric_sense.doctype.tailoring_sheet.tailoring_sheet.get_remaining_quantities",
		args: {
			tailoring_sheet: frm.doc.name,
		},
		callback: function (r) {
			if (r.message) {
				// Create new Material Request
				frappe.model.with_doctype("Material Request", function () {
					let mr = frappe.model.get_new_doc("Material Request");
					mr.material_request_type = "Purchase";
					mr.custom_tailoring_sheet = frm.doc.name;
					mr.transaction_date = frappe.datetime.get_today();

					// Check if all remaining quantities are 0
					let all_zero = true;

					// Store items to add
					// Service items are already filtered by server-side method
					let items_to_add = [];
					r.message.items.forEach(function (item) {
						if (item.remaining_qty > 0) {
							all_zero = false;
							items_to_add.push({
								item_code: item.item_code,
								qty: item.remaining_qty,
							});
						}
					});

					// Set manager approval status if all quantities are 0
					if (all_zero) {
						mr.custom_manager_approval_status = "Pending";
						mr.custom_is_additional = 1;
					} else {
						mr.custom_manager_approval_status = "Approved";
					}

					// Navigate to the new Material Request
					frappe.set_route("Form", "Material Request", mr.name);

					// Add items after form is loaded to ensure field triggers work
					setTimeout(function () {
						if (
							cur_frm &&
							cur_frm.doctype === "Material Request" &&
							cur_frm.doc.name === mr.name
						) {
							items_to_add.forEach(function (item_data) {
								let row = frappe.model.add_child(cur_frm.doc, "items");
								frappe.model
									.set_value(
										row.doctype,
										row.name,
										"item_code",
										item_data.item_code
									)
									.then(() => {
										frappe.model.set_value(
											row.doctype,
											row.name,
											"qty",
											item_data.qty
										);
										frappe.model.set_value(
											row.doctype,
											row.name,
											"schedule_date",
											frappe.datetime.add_days(
												frappe.datetime.get_today(),
												7
											)
										);
									});
							});
							cur_frm.refresh_field("items");
						}
					}, 500);
				});
			}
		},
	});
};
