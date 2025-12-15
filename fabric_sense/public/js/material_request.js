frappe.ui.form.on("Material Request", {
	refresh: function (frm) {
		// Save the original function
		const original_make_purchase_order = frm.events.make_purchase_order;

		// Override the function
		frm.events.make_purchase_order = function () {
			// Call the server-side method directly without showing the supplier selection popup
			frappe.model.open_mapped_doc({
				method: "erpnext.stock.doctype.material_request.material_request.make_purchase_order",
				frm: frm,
				args: {},
				run_link_triggers: true,
			});
		};

		const pageActions = frm.page.page_actions;
		pageActions.find(".btn-primary").each(function () {
			const btnText = $(this).text().trim();
			if (
				btnText === "Approve" ||
				btnText === "Reject" ||
				btnText === "Resubmit for Manager Approval"
			) {
				$(this).remove();
			}
		});
		// Check if logged-in user has Manager role and approval status is Pending
		if (
			frappe.user.has_role("Sales Manager") &&
			frm.doc.custom_manager_approval_status === "Pending" &&
			!frm.is_new()
		) {
			// Add Approve button
			frm.add_custom_button(__("Approve"), function () {
				frappe.confirm(
					__("Are you sure you want to approve this Material Request?"),
					function () {
						// On confirm
						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: "Material Request",
								name: frm.doc.name,
								fieldname: "custom_manager_approval_status",
								value: "Approved",
							},
							callback: function (response) {
								if (!response.exc) {
									frappe.msgprint({
										title: __("Success"),
										indicator: "green",
										message: __("Material Request has been approved"),
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
					__("Are you sure you want to reject this Material Request?"),
					function () {
						// On confirm
						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: "Material Request",
								name: frm.doc.name,
								fieldname: "custom_manager_approval_status",
								value: "Rejected",
							},
							callback: function (response) {
								if (!response.exc) {
									frappe.msgprint({
										title: __("Success"),
										indicator: "green",
										message: __("Material Request has been rejected"),
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
		if (
			frappe.user.has_role("Sales User") &&
			frm.doc.custom_manager_approval_status === "Rejected" &&
			!frm.is_new()
		) {
			// Add Resubmit button
			frm.add_custom_button(__("Resubmit for Manager Approval"), function () {
				frappe.confirm(
					__(
						"Are you sure you want to resubmit this Material Request for Manager Approval?"
					),
					function () {
						// On confirm
						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: "Material Request",
								name: frm.doc.name,
								fieldname: "custom_manager_approval_status",
								value: "Pending",
							},
							callback: function (response) {
								if (!response.exc) {
									frappe.msgprint({
										title: __("Success"),
										indicator: "green",
										message: __("Material Request has been resubmitted"),
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
		if (frm.doc.custom_manager_approval_status === "Pending") {
			frappe.msgprint({
				title: __("Manager Approval Required"),
				indicator: "red",
				message: __(
					"This is an additional material request. Manager approval is needed to submit this material request."
				),
			});
			frappe.validated = false;
		}
		if (frm.doc.custom_manager_approval_status === "Rejected") {
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

