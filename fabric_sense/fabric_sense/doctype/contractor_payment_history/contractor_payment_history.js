frappe.ui.form.on("Contractor Payment History", {
	refresh(frm) {
		const pageActions = frm.page.page_actions;
		pageActions.find(".btn-primary").each(function () {
			const btnText = $(this).text().trim();
			if (btnText === "Make Payment") {
				$(this).remove();
			}
		});
		if (frm.doc.status === "Unpaid" && !frm.is_new()) {
			// Add payment button
			frm.add_custom_button(__("Make Payment"), function () {
				frappe.confirm(
					__("Are you sure you want to make payment?"),
					function () {
						// On confirm
					},
					function () {
						// On cancel - do nothing
					}
				);
			})
				.addClass("btn-primary")
				.prependTo(frm.page.page_actions);
		}
	},
});
