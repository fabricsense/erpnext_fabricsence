// Copyright (c) 2025, innogenio and contributors
// For license information, please see license.txt

frappe.require("/assets/fabric_sense/js/helpers/measurement_sheet_helpers.js");

const msHelper = fabric_sense.measurement_sheet;

frappe.ui.form.on("Measurement Sheet", {
	onload(frm) {
		frm.refresh_field("measurement_details");

		// Ensure Project is filtered by the selected Customer on load
		frm.set_query("project", () => ({
			filters: { customer: frm.doc.customer || undefined }
		}));

		if (frm.is_new() && !frm.doc.name && !frm._child_table_initialized) {
			let should_clear = true;
			if (frm.doc.measurement_details && frm.doc.measurement_details.length > 0) {
				for (let row of frm.doc.measurement_details) {
					if (row.area || row.product_type || row.width) {
						should_clear = false;
						break;
					}
				}
			}

			if (should_clear) {
				frm.clear_table("measurement_details");
				frm.refresh_field("measurement_details");
				frm.set_value("total_amount", 0);
			}

			frm._child_table_initialized = true;
		}
	},

	// When Customer changes, clear Project and re-apply query filter
	customer(frm) {
		frm.set_query("project", () => ({
			filters: { customer: frm.doc.customer || undefined }
		}));
		if (frm.doc.project) {
			frm.set_value("project", null);
		}
		// Clear item rate cache when customer changes to force re-fetch with new price list
		msHelper.clearItemRateCache?.();
		// Clear stock cache as well
		msHelper.clearStockCache?.();
	},

	refresh(frm) {
		msHelper.setup_custom_actions(frm);
		msHelper.apply_item_filters(frm);
		msHelper.clearItemRateCache?.();
		msHelper.clearStockCache?.();

		// Keep Project filtered by Customer on refresh as well
		frm.set_query("project", () => ({
			filters: { customer: frm.doc.customer || undefined }
		}));

		frm.refresh_field("measurement_details");

		if (frm.doc.measurement_method === "Contractor Assigned") {
			frm.toggle_display("contractor_assignment_section", true);
			frm.toggle_display("assigned_contractor", true);
			frm.toggle_display("expected_measurement_date", true);
			frm.toggle_display("actual_measurement_date", true);
			frm.toggle_display("site_visit_required", true);

			setTimeout(() => {
				frm.refresh_field("contractor_assignment_section");
				frm.refresh_field("assigned_contractor");
				frm.refresh_field("expected_measurement_date");
				frm.refresh_field("actual_measurement_date");
				frm.refresh_field("site_visit_required");
				frm.refresh_field("visiting_charge");
			}, 100);
		} else {
			frm.toggle_display("contractor_assignment_section", false);
			frm.toggle_display("actual_measurement_date", false);
		}

		// Add "Create Sales Order" button when Measurement Sheet is Approved and saved
		msHelper.create_sales_order_from_measurement_sheet(frm);

		msHelper.calculate_totals(frm);
	},

	measurement_method(frm) {
		if (frm.doc.measurement_method === "Contractor Assigned") {
			frm.set_df_property("assigned_contractor", "reqd", 1);
			frm.set_df_property("expected_measurement_date", "reqd", 1);

			frm.toggle_display("contractor_assignment_section", true);
			frm.toggle_display("assigned_contractor", true);
			frm.toggle_display("expected_measurement_date", true);
			frm.toggle_display("actual_measurement_date", true);
			frm.toggle_display("site_visit_required", true);

			setTimeout(() => {
				frm.refresh_field("contractor_assignment_section");
				frm.refresh_field("assigned_contractor");
				frm.refresh_field("expected_measurement_date");
				frm.refresh_field("actual_measurement_date");
				frm.refresh_field("site_visit_required");
				frm.refresh_field("visiting_charge");
			}, 100);
		} else {
			// Customer Provided - clear all contractor-related fields
			frm.set_df_property("assigned_contractor", "reqd", 0);
			frm.set_df_property("expected_measurement_date", "reqd", 0);
			frm.set_df_property("visiting_charge", "reqd", 0);

			// Clear field values
			frm.set_value("site_visit_required", 0);
			frm.set_value("visiting_charge", 0);
			frm.set_value("assigned_contractor", "");
			frm.set_value("expected_measurement_date", "");

			frm.toggle_display("contractor_assignment_section", false);
			frm.toggle_display("assigned_contractor", false);
			frm.toggle_display("expected_measurement_date", false);
			frm.toggle_display("actual_measurement_date", false);
			frm.toggle_display("site_visit_required", false);

			setTimeout(() => {
				frm.refresh_field("assigned_contractor");
				frm.refresh_field("expected_measurement_date");
				frm.refresh_field("actual_measurement_date");
				frm.refresh_field("site_visit_required");
				frm.refresh_field("visiting_charge");
			}, 100);
		}

		frm.refresh_field("measurement_details");
	},

	site_visit_required(frm) {
		if (frm.doc.site_visit_required) {
			frm.set_df_property("visiting_charge", "reqd", 1);
		} else {
			frm.set_df_property("visiting_charge", "reqd", 0);
			frm.set_value("visiting_charge", 0);
		}
		msHelper.calculate_totals(frm);
	},

	visiting_charge(frm) {
		msHelper.calculate_totals(frm);
	},

	status(frm) {
		if (frm.doc.status === "Rejected") {
			frm.set_df_property("rejection_reason", "reqd", 1);
		} else {
			frm.set_df_property("rejection_reason", "reqd", 0);
		}
		// Ensure status field is not read-only
		frm.set_df_property("status", "read_only", 0);
	},

	after_save(frm) {
		// Refresh status field after save to ensure it displays the saved value
		// Reload the document to get the actual saved status from database
		frm.reload_doc();
	}
});

// Handle child table events - listen from parent form context
frappe.ui.form.on("Measurement Detail", {
	refresh(frm) {
		msHelper.apply_item_filters(frm);
		msHelper.clearItemRateCache?.();
		msHelper.clearStockCache?.();
	},

	async product_type(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		// Store previous product type before resetting fields
		// Note: row.product_type is already updated to the new value at this point
		// So we need to check if fabric fields are being cleared
		msHelper.reset_fields_for_product_type(row);

		// Remove highlighting when product type changes away from Window Curtains/Roman Blinds
		// (fabric fields are cleared in reset_fields_for_product_type)
		if (!["Window Curtains", "Roman Blinds"].includes(row.product_type)) {
			msHelper.highlight_fabric_field(frm, cdt, cdn, false);
		}

		// If switching to/from Window Curtains/Roman Blinds and stitching_pattern exists, recalculate stitching_charge
		if (row.stitching_pattern) {
			const rate = await msHelper.fetch_item_rate(row.stitching_pattern, null, frm);
			let stitching_charge = rate || 0;
			if (row.product_type === "Window Curtains") {
				const panels = parseFloat(row.panels) || 0;
				stitching_charge = panels * (rate || 0);
			} else if (row.product_type === "Roman Blinds") {
				const sqft = parseFloat(row.square_feet) || 0;
				stitching_charge = sqft * (rate || 0);
			}
			await frappe.model.set_value(cdt, cdn, "stitching_charge", stitching_charge);
		}

		setTimeout(() => {
			frm.refresh_field("stitching_pattern", cdn, "measurement_details");
			frm.refresh_field("stitching_charge", cdn, "measurement_details");
			frm.refresh_field("measurement_details");
		}, 50);

		msHelper.batch_calculate_row(frm, cdt, cdn);
	},

	async width(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.product_type === "Window Curtains" || row.product_type === "Tracks/Rods") {
			msHelper.calculate_track_rod_qty(frm, cdt, cdn);
		} else {
			msHelper.batch_calculate_row(frm, cdt, cdn);
			
			// For Roman Blinds, recalculate stitching_charge if stitching_pattern exists
			if (row.product_type === "Roman Blinds" && row.stitching_pattern) {
				// Wait for square_feet to be calculated by batch_calculate_row
				setTimeout(async () => {
					const rate = await msHelper.fetch_item_rate(row.stitching_pattern, null, frm);
					const sqft = parseFloat(row.square_feet) || 0;
					const stitching_charge = sqft * (rate || 0);
					await frappe.model.set_value(cdt, cdn, "stitching_charge", stitching_charge);
					frm.refresh_field("measurement_details");
				}, 100);
			}
		}
	},

	async height(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.product_type === "Window Curtains") {
			msHelper.calculate_fabric_qty(frm, cdt, cdn);
			msHelper.calculate_row_amounts(frm, cdt, cdn);
		} else {
			msHelper.batch_calculate_row(frm, cdt, cdn);
			
			// For Roman Blinds, recalculate stitching_charge if stitching_pattern exists
			if (row.product_type === "Roman Blinds" && row.stitching_pattern) {
				// Wait for square_feet to be calculated by batch_calculate_row
				setTimeout(async () => {
					const rate = await msHelper.fetch_item_rate(row.stitching_pattern, null, frm);
					const sqft = parseFloat(row.square_feet) || 0;
					const stitching_charge = sqft * (rate || 0);
					await frappe.model.set_value(cdt, cdn, "stitching_charge", stitching_charge);
					frm.refresh_field("measurement_details");
				}, 100);
			}
		}
	},

	async panels(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		
		// Client-side validation: Panel must be > 0 for Window Curtains and Roman Blinds
		if (row.product_type === "Window Curtains" || row.product_type === "Roman Blinds") {
			const panelsValue = parseFloat(row.panels) || 0;
			if (panelsValue <= 0) {
				frappe.msgprint({
					title: __("Invalid Panel Value"),
					message: __("Panel must be greater than 0. Please enter a valid quantity."),
					indicator: "red"
				});
				// Clear the invalid value
				await frappe.model.set_value(cdt, cdn, "panels", "");
				return;
			}
		}
		
		// Recalculate stitching_charge if stitching_pattern exists and product type is Window Curtains
		if (row.product_type === "Window Curtains" && row.stitching_pattern) {
			const rate = await msHelper.fetch_item_rate(row.stitching_pattern, null, frm);
			const panels = parseFloat(row.panels) || 0;
			const stitching_charge = panels * (rate || 0);
			await frappe.model.set_value(cdt, cdn, "stitching_charge", stitching_charge);
		}
		
		// All three functions now call calculate_row_amounts internally
		// Await them to ensure proper sequencing and avoid race conditions
		await msHelper.calculate_fabric_qty(frm, cdt, cdn);
		await msHelper.calculate_lead_rope_qty(frm, cdt, cdn);
		await msHelper.calculate_track_rod_qty(frm, cdt, cdn);
		// Note: calculate_row_amounts is already called by each function above
		// The setTimeout is removed to avoid redundant calculations
	},

	adjust(frm, cdt, cdn) {
		msHelper.calculate_fabric_qty(frm, cdt, cdn);
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	async fabric_selected(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		
		// Clear highlighting if fabric is cleared
		if (!row.fabric_selected) {
			msHelper.highlight_fabric_field(frm, cdt, cdn, false);
			// Clear stock cache for this item
			msHelper.clearStockCache?.();
		}
		
		const rate = row.fabric_selected ? await msHelper.fetch_item_rate(row.fabric_selected, null, frm) : 0;
		await frappe.model.set_value(cdt, cdn, "fabric_rate", rate || 0);
		msHelper.calculate_row_amounts(frm, cdt, cdn);
		
		// Check stock availability when fabric is selected
		if (row.fabric_selected) {
			// Check stock immediately (even if qty is 0, to see if any stock exists)
			const stock_result = await msHelper.check_fabric_stock_availability(frm, cdt, cdn);
			if (!stock_result.is_available) {
				msHelper.highlight_fabric_field(frm, cdt, cdn, true);
				msHelper.show_fabric_stock_warning(frm, cdt, cdn, stock_result.available_qty, stock_result.required_qty, stock_result.fabric_name);
			} else {
				msHelper.highlight_fabric_field(frm, cdt, cdn, false);
			}
		}
	},

	async fabric_qty(frm, cdt, cdn) {
		msHelper.calculate_row_amounts(frm, cdt, cdn);
		
		// Check stock availability when fabric_qty changes
		const row = locals[cdt][cdn];
		if (row.fabric_selected && row.fabric_qty) {
			const stock_result = await msHelper.check_fabric_stock_availability(frm, cdt, cdn);
			if (!stock_result.is_available) {
				msHelper.highlight_fabric_field(frm, cdt, cdn, true);
				msHelper.show_fabric_stock_warning(frm, cdt, cdn, stock_result.available_qty, stock_result.required_qty, stock_result.fabric_name);
			} else {
				msHelper.highlight_fabric_field(frm, cdt, cdn, false);
			}
		}
	},

	lining_qty(frm, cdt, cdn) {
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	fabric_rate(frm, cdt, cdn) {
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	async lining(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		const rate = row.lining ? await msHelper.fetch_item_rate(row.lining, null, frm) : 0;
		await frappe.model.set_value(cdt, cdn, "lining_rate", rate || 0);
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	lining_rate(frm, cdt, cdn) {
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	async lead_rope(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.lead_rope) {
			const rate = await msHelper.fetch_item_rate(row.lead_rope, null, frm);
			await frappe.model.set_value(cdt, cdn, "lead_rope_rate", rate || 0);
		}
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	lead_rope_qty(frm, cdt, cdn) {
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	lead_rope_rate(frm, cdt, cdn) {
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	async track_rod(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.track_rod) {
			const rate = await msHelper.fetch_item_rate(row.track_rod, null, frm);
			await frappe.model.set_value(cdt, cdn, "track_rod_rate", rate || 0);
		}
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	track_rod_type(frm, cdt, cdn) {
		msHelper.calculate_track_rod_qty(frm, cdt, cdn);
	},

	track_rod_qty(frm, cdt, cdn) {
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	track_rod_rate(frm, cdt, cdn) {
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	selection(frm, cdt, cdn) {
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	async stitching_pattern(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		const rate = row.stitching_pattern ? await msHelper.fetch_item_rate(row.stitching_pattern, null, frm) : 0;
		
		// For Window Curtains: Stitching Charge = Panels × Rate
		// For Roman Blinds: Stitching Charge = Sqft × Rate
		// For other product types: Stitching Charge = Rate
		let stitching_charge = rate || 0;
		if (row.product_type === "Window Curtains") {
			const panels = parseFloat(row.panels) || 0;
			stitching_charge = panels * (rate || 0);
		} else if (row.product_type === "Roman Blinds") {
			const sqft = parseFloat(row.square_feet) || 0;
			stitching_charge = sqft * (rate || 0);
		}
		
		await frappe.model.set_value(cdt, cdn, "stitching_charge", stitching_charge);
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	stitching_charge(frm, cdt, cdn) {
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	async fitting_type(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		const rate = row.fitting_type ? await msHelper.fetch_item_rate(row.fitting_type, null, frm) : 0;
		await frappe.model.set_value(cdt, cdn, "fitting_charge", rate || 0);
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	fitting_charge(frm, cdt, cdn) {
		msHelper.calculate_row_amounts(frm, cdt, cdn);
	},

	measurement_details_add(frm, cdt, cdn) {
		msHelper.apply_item_filters(frm);
		setTimeout(() => {
			const row = locals[cdt][cdn];
			if (row.product_type === "Window Curtains" && row.panels != null && row.panels !== "") {
				msHelper.calculate_lead_rope_qty(frm, cdt, cdn);
			}
		}, 100);
	},

	measurement_details_remove(frm) {
		msHelper.calculate_totals(frm);
	},

	amount(frm) {
		msHelper.calculate_totals(frm);
	}
});

