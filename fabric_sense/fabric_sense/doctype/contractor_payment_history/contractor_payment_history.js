// contractor_payment_history.js
frappe.ui.form.on("Contractor Payment History", {
	refresh(frm) {
		// Remove duplicate buttons on page refresh
		const pageActions = frm.page.page_actions;
		pageActions.find(".btn-primary").each(function () {
			const btnText = $(this).text().trim();
			if (btnText === "Make Payment") {
				$(this).remove();
			}
		});

		// Show "Make Payment" button for Unpaid or Partially Paid status
		if ((frm.doc.status === "Unpaid" || frm.doc.status === "Partially Paid") && !frm.is_new()) {
			frm.add_custom_button(__("Make Payment"), function () {
				frm.events.make_single_payment(frm);
			})
				.addClass("btn-primary")
				.prependTo(frm.page.page_actions);
		}
	},

	make_single_payment(frm) {
		// Validate contractor and balance
		if (!frm.doc.contractor) {
			frappe.msgprint(__("Contractor is required"));
			return;
		}

		if (!frm.doc.balance || frm.doc.balance <= 0) {
			frappe.msgprint(__("No balance amount to pay"));
			return;
		}

		// Use ERPNext's standard make_mapped_doc approach
		frappe.model.open_mapped_doc({
			method: "fabric_sense.fabric_sense.doctype.contractor_payment_history.contractor_payment_history.make_payment_entry",
			frm: frm
		});
	}
});