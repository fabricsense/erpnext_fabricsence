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

		// Show "Make Payment" button only for Unpaid status
		if (frm.doc.status === "Unpaid" && !frm.is_new()) {
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

		// Create Payment Entry using model API
		frappe.model.with_doctype("Payment Entry", function() {
			let payment_doc = frappe.model.get_new_doc("Payment Entry");
			
			// Set all fields directly on the doc object first
			payment_doc.payment_type = "Pay";
			payment_doc.party_type = "Employee";  // Force Employee
			payment_doc.party = frm.doc.contractor;
			payment_doc.paid_amount = frm.doc.balance;
			payment_doc.received_amount = frm.doc.balance;
			payment_doc.remarks = `Payment for Task: ${frm.doc.task || ""}, Project: ${frm.doc.project || ""}`;
			payment_doc.custom_contractor_payment_history = frm.doc.name;
			
			// Store in sessionStorage to be picked up by payment_entry.js
			sessionStorage.setItem("force_party_type_employee", "1");
			sessionStorage.setItem("contractor_payment_ref", frm.doc.name);
			sessionStorage.setItem("contractor_party", frm.doc.contractor);
			sessionStorage.setItem("contractor_balance", frm.doc.balance);
			sessionStorage.setItem("contractor_task", frm.doc.task || "");
			sessionStorage.setItem("contractor_project", frm.doc.project || "");
			
			// Navigate to the form
			frappe.set_route("Form", "Payment Entry", payment_doc.name);
		});
	}
});