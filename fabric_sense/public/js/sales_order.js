frappe.ui.form.on("Sales Order", {
	refresh: function (frm) {
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

		// Add Measurement Sheet connection to dashboard
		if (frm.doc.measurement_sheet && !frm.is_new()) {
			// Try multiple times with different delays
			setTimeout(() => add_measurement_sheet_connection(frm), 500);
			setTimeout(() => add_measurement_sheet_connection(frm), 1500);
			setTimeout(() => add_measurement_sheet_connection(frm), 3000);
			
			// Also add when connections tab is clicked
			$(document).on('click', '[data-fieldname="connections"]', function() {
				setTimeout(() => add_measurement_sheet_connection(frm), 200);
			});
		}

		// Check if logged-in user has Manager role and approval status is Pending
		if (
			frappe.user.has_role("Sales Manager") &&
			frm.doc.manager_approval_status === "Pending" &&
			!frm.is_new()
		) {
			// Add Approve button
			frm.add_custom_button(__("Approve"), function () {
				frappe.confirm(
					__("Are you sure you want to approve this Sales Order?"),
					function () {
						// On confirm
						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: "Sales Order",
								name: frm.doc.name,
								fieldname: "manager_approval_status",
								value: "Approved",
							},
							callback: function (response) {
								if (!response.exc) {
									frappe.msgprint({
										title: __("Success"),
										indicator: "green",
										message: __("Sales order has been approved"),
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
					__("Are you sure you want to reject this Sales Order?"),
					function () {
						// On confirm
						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: "Sales Order",
								name: frm.doc.name,
								fieldname: "manager_approval_status",
								value: "Rejected",
							},
							callback: function (response) {
								if (!response.exc) {
									frappe.msgprint({
										title: __("Success"),
										indicator: "green",
										message: __("Sales Order has been rejected"),
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
			frm.doc.manager_approval_status === "Rejected" &&
			!frm.is_new()
		) {
			// Add Resubmit button
			frm.add_custom_button(__("Resubmit for Manager Approval"), function () {
				frappe.confirm(
					__("Are you sure you want to resubmit this Sales Order for Manager Approval?"),
					function () {
						// On confirm
						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: "Sales Order",
								name: frm.doc.name,
								fieldname: "manager_approval_status",
								value: "Pending",
							},
							callback: function (response) {
								if (!response.exc) {
									frappe.msgprint({
										title: __("Success"),
										indicator: "green",
										message: __("Sales Order has been resubmitted"),
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

		// ========================================
		// CUSTOM MATERIAL REQUEST BUTTON
		// ========================================

		// Override the default Material Request button
		if (frm.doc.docstatus === 1) {
			// Remove the default Material Request button if it exists
			frm.remove_custom_button("Material Request", "Create");

			// Add our custom Material Request button
			frm.add_custom_button(
				__("Material Request"),
				function () {
					// Call the server method to get the mapped document data
					frappe.call({
						method: "fabric_sense.fabric_sense.py.sales_order.make_material_request",
						args: {
							source_name: frm.doc.name,
						},
						callback: function (r) {
							if (r.message) {
								// Create a new Material Request form with the mapped data
								var doc = frappe.model.sync(r.message);
								frappe.set_route("Form", doc[0].doctype, doc[0].name);
							}
						},
					});
				},
				__("Create")
			);
		}

		// Check if status is "To Deliver"
		if (frm.doc.status === "To Deliver" && frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Send Order Ready Notification"), function () {
				// Call server-side Python function
				frappe.call({
					method: "fabric_sense.fabric_sense.py.sales_order.send_order_ready_notification",
					args: {
						sales_order: frm.doc.name
					},
					callback: function(r) {
						if (!r.exc) {
							frappe.msgprint({
								title: __("Success"),
								indicator: "green",
								message: __("Order ready notification sent to customer")
							});
						}
					}
				});
			}).addClass("btn-primary");
		}
	},

	before_submit: function (frm) {
		// Block submission if status is Pending
		if (frm.doc.manager_approval_status === "Pending") {
			frappe.msgprint({
				title: __("Approval Pending"),
				indicator: "orange",
				message: __(
					"Manager approval is pending. Manager approval is needed to submit this sales order."
				),
			});
			frappe.validated = false;
			return false;
		}

		// Block submission if status is Rejected
		if (frm.doc.manager_approval_status === "Rejected") {
			frappe.msgprint({
				title: __("Approval Rejected"),
				indicator: "red",
				message: __(
					"Manager rejected this record.Update and resubmit this record for manager approval."
				),
			});
			frappe.validated = false;
			return false;
		}
	},
});

function add_measurement_sheet_connection(frm) {
	// Multiple attempts to find the connections area
	let connectionsArea = $('.form-dashboard[data-doctype="Sales Order"]');
	
	if (connectionsArea.length === 0) {
		connectionsArea = $('.form-dashboard');
	}
	
	if (connectionsArea.length === 0) {
		connectionsArea = $('[data-fieldname="connections"] .form-dashboard-wrapper');
	}
	
	if (connectionsArea.length === 0) {
		// Try to find any dashboard wrapper
		connectionsArea = $('.form-dashboard-wrapper');
	}

	console.log("Connections area found:", connectionsArea.length);
	
	if (connectionsArea.length === 0) return;

	// Check if we already added the connection
	if (connectionsArea.find('.measurement-sheet-connection').length > 0) return;

	// Create a simple connection section that matches ERPNext style
	const sourceSection = `
		<div class="measurement-sheet-connection" style="margin-bottom: 15px;">
			<div class="form-dashboard-section">
				<div class="section-head">
					<h5 class="uppercase"><b>${__("Source")}</b></h5>
				</div>
				<div class="section-body">
					<div class="document-link" data-doctype="Measurement Sheet">
						<a href="/app/measurement-sheet/${frm.doc.measurement_sheet}" class="btn-open no-decoration" title="${__('Open Measurement Sheet')}">
							<span class="count">1</span>
							${__("Measurement Sheet")}
						</a>
					</div>
				</div>
			</div>
		</div>
	`;

	// Add the section to the connections area
	connectionsArea.prepend(sourceSection);
	console.log("Added measurement sheet connection");
}
