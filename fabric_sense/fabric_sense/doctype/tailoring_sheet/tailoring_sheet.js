// All functions are now in fabric_sense.tailoring_sheet namespace
// Loaded via hooks.py from /public/js/helpers/tailoring_sheet_helpers.js

frappe.ui.form.on("Tailoring Sheet", {
	refresh(frm) {
		fabric_sense.tailoring_sheet.setup_tailoring_sheet_form(frm);
	},
	measurement_sheet(frm) {
		fabric_sense.tailoring_sheet.handle_measurement_sheet_change(frm);
	},
});

// Child table event handlers for Tailoring Measurement Details
frappe.ui.form.on("Tailoring Measurement Details", {
	fabric_adjust(frm, cdt, cdn) {
		fabric_sense.tailoring_sheet.calculate_fabric_adjust(cdt, cdn);
	},

	lining_adjust(frm, cdt, cdn) {
		fabric_sense.tailoring_sheet.calculate_lining_adjust(cdt, cdn);
	},

	final_fabric_quantity(frm, cdt, cdn) {
		fabric_sense.tailoring_sheet.calculate_final_fabric_quantity(cdt, cdn);
	},

	final_lining_quantity(frm, cdt, cdn) {
		fabric_sense.tailoring_sheet.calculate_final_lining_quantity(cdt, cdn);
	},

	fabric_amount(frm, cdt, cdn) {
		fabric_sense.tailoring_sheet.calculate_fabric_amount(cdt, cdn);
	},

	lining_amount(frm, cdt, cdn) {
		fabric_sense.tailoring_sheet.calculate_lining_amount(cdt, cdn);
	},
});
