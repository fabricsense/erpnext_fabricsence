frappe.ui.form.on("Payment Entry", {
	refresh: function (frm) {
		// Remove existing custom buttons to prevent duplicates
		const pageActions = frm.page.page_actions;
		pageActions.find(".btn-primary").each(function () {
			const btnText = $(this).text().trim();
			if (
				btnText === "Approve Discount" ||
				btnText === "Reject Discount" ||
				btnText === "Approve" ||
				btnText === "Reject" ||
				btnText === "Resubmit Payment for Discount Approval" ||
				btnText === "Resubmit for Manager Approval"
			) {
				$(this).remove();
			}
		});

		// Scenario 1: Sales Manager + Discount Approval Pending
		// Show: Approve Discount, Reject Discount
		if (
			frappe.user.has_role("Sales Manager") &&
			frm.doc.custom_manager_approval_status === "Discount Approval Pending" &&
			!frm.is_new()
		) {
			// Add Approve button
			frm.add_custom_button(__("Approve Discount"), function () {
				frappe.confirm(
					__("Are you sure you want to approve this Payment Entry?"),
					function () {
						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: "Payment Entry",
								name: frm.doc.name,
								fieldname: "custom_manager_approval_status",
								value: "Discount Approved",
							},
							callback: function (response) {
								if (!response.exc) {
									frappe.msgprint({
										title: __("Success"),
										indicator: "green",
										message: __("Payment Entry has been approved"),
									});
									frm.reload_doc();
								}
							},
						});
					},
					function () {
						// On cancel - do nothing
					}
				);
			})
				.addClass("btn-primary")
				.prependTo(frm.page.page_actions);

			// Add Reject button
			frm.add_custom_button(__("Reject Discount"), function () {
				frappe.confirm(
					__("Are you sure you want to reject this Payment Entry?"),
					function () {
						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: "Payment Entry",
								name: frm.doc.name,
								fieldname: "custom_manager_approval_status",
								value: "Discount Rejected",
							},
							callback: function (response) {
								if (!response.exc) {
									frappe.msgprint({
										title: __("Success"),
										indicator: "green",
										message: __("Payment Entry has been rejected"),
									});
									frm.reload_doc();
								}
							},
						});
					},
					function () {
						// On cancel - do nothing
					}
				);
			})
				.addClass("btn-primary")
				.prependTo(frm.page.page_actions);
		}

		// Scenario 2: Manager Approval Status = Pending or Discount Approved
		// Show: Approve, Reject
		if (
			frappe.user.has_role("Sales Manager") &&
			(frm.doc.custom_manager_approval_status === "Pending" ||
				frm.doc.custom_manager_approval_status === "Discount Approved") &&
			!frm.is_new()
		) {
			// Add Approve button
			frm.add_custom_button(__("Approve"), function () {
				frappe.confirm(
					__("Are you sure you want to approve this Payment Entry?"),
					function () {
						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: "Payment Entry",
								name: frm.doc.name,
								fieldname: "custom_manager_approval_status",
								value: "Approved",
							},
							callback: function (response) {
								if (!response.exc) {
									frappe.msgprint({
										title: __("Success"),
										indicator: "green",
										message: __("Payment Entry has been approved"),
									});
									frm.reload_doc();
								}
							},
						});
					},
					function () {
						// On cancel - do nothing
					}
				);
			})
				.addClass("btn-primary")
				.prependTo(frm.page.page_actions);

			// Add Reject button
			frm.add_custom_button(__("Reject"), function () {
				frappe.confirm(
					__("Are you sure you want to reject this Payment Entry?"),
					function () {
						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: "Payment Entry",
								name: frm.doc.name,
								fieldname: "custom_manager_approval_status",
								value: "Rejected",
							},
							callback: function (response) {
								if (!response.exc) {
									frappe.msgprint({
										title: __("Success"),
										indicator: "green",
										message: __("Payment Entry has been rejected"),
									});
									frm.reload_doc();
								}
							},
						});
					},
					function () {
						// On cancel - do nothing
					}
				);
			})
				.addClass("btn-primary")
				.prependTo(frm.page.page_actions);
		}

		// Scenario 3: Sales User + Discount Rejected
		// Show: Resubmit Payment for Discount Approval
		if (
			frappe.user.has_role("Sales User") &&
			frm.doc.custom_manager_approval_status === "Discount Rejected" &&
			!frm.is_new()
		) {
			frm.add_custom_button(__("Resubmit Payment for Discount Approval"), function () {
				frappe.confirm(
					__(
						"Are you sure you want to resubmit this Payment Entry for discount approval?"
					),
					function () {
						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: "Payment Entry",
								name: frm.doc.name,
								fieldname: "custom_manager_approval_status",
								value: "Discount Approval Pending",
							},
							callback: function (response) {
								if (!response.exc) {
									frappe.msgprint({
										title: __("Success"),
										indicator: "green",
										message: __(
											"Payment Entry has been resubmitted for discount approval"
										),
									});
									frm.reload_doc();
								}
							},
						});
					},
					function () {
						// On cancel - do nothing
					}
				);
			})
				.addClass("btn-primary")
				.prependTo(frm.page.page_actions);
		}

		// Scenario 4: Sales User + Rejected
		// Show: Resubmit for Manager Approval
		// Logic: Set to "Discount Approval Pending" if deductions exist, otherwise "Pending"
		if (
			frappe.user.has_role("Sales User") &&
			frm.doc.custom_manager_approval_status === "Rejected" &&
			!frm.is_new()
		) {
			frm.add_custom_button(__("Resubmit for Manager Approval"), function () {
				frappe.confirm(
					__(
						"Are you sure you want to resubmit this Payment Entry for manager approval?"
					),
					function () {
						// Check if deductions table has data
						let hasDeductions = frm.doc.deductions && frm.doc.deductions.length > 0;
						let newStatus = hasDeductions ? "Discount Approval Pending" : "Pending";

						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: "Payment Entry",
								name: frm.doc.name,
								fieldname: "custom_manager_approval_status",
								value: newStatus,
							},
							callback: function (response) {
								if (!response.exc) {
									frappe.msgprint({
										title: __("Success"),
										indicator: "green",
										message: __(
											"Payment Entry has been resubmitted for manager approval"
										),
									});
									frm.reload_doc();
								}
							},
						});
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
	before_submit: function (frm) {
		// Check if custom_manager_approval_status is Pending
		if (
			frm.doc.custom_manager_approval_status === "Pending" ||
			frm.doc.custom_manager_approval_status === "Discount Approval Pending" ||
			frm.doc.custom_manager_approval_status === "Discount Approved"
		) {
			frappe.msgprint({
				title: __("Manager Approval Required"),
				indicator: "red",
				message: __("Manager approval is needed to submit this payment."),
			});
			frappe.validated = false;
		}
		if (
			frm.doc.custom_manager_approval_status === "Rejected" ||
			frm.doc.custom_manager_approval_status === "Discount Rejected"
		) {
			frappe.msgprint({
				title: __("Manager Rejected"),
				indicator: "red",
				message: __(
					"Manager rejected this record.Update and resubmit this record for manager approval."
				),
			});
			frappe.validated = false;
		}
	},
});
