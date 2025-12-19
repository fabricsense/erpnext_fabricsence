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
			$(document).on("click", '[data-fieldname="connections"]', function () {
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
			// Use setTimeout to ensure this runs after ERPNext's default buttons are added
			setTimeout(() => {
				// Remove all Material Request buttons (both default and custom)
				frm.remove_custom_button("Material Request", "Create");
				frm.remove_custom_button("Material Request");
				frm.remove_custom_button("Additional Material Request", "Create");
				frm.remove_custom_button("Additional Material Request");

				// Also remove any existing Multi Material Request buttons
				frm.remove_custom_button("Multi Material Request", "Create");
				frm.remove_custom_button("Multi Material Request");

				// Check if remaining items exist and show appropriate button
				check_remaining_items_and_show_button(frm);
			}, 100);
		}

		// Hide "Update Items" button if manager approval status is "Approved"
		if (frm.doc.manager_approval_status === "Approved") {
			// Remove the "Update Items" button from the page actions
			setTimeout(() => {
				const pageActions = frm.page.page_actions;
				pageActions.find(".btn").each(function () {
					const btnText = $(this).text().trim();
					if (btnText === "Update Items") {
						$(this).remove();
					}
				});
			}, 100);
		}

		// Check if status is "To Deliver" or "To Deliver and Bill"
		if (
			(frm.doc.status === "To Deliver" || frm.doc.status === "To Deliver and Bill") &&
			frm.doc.docstatus === 1
		) {
			frm.add_custom_button(__("Send Order Ready Notification"), function () {
				// Call server-side Python function
				frappe.call({
					method: "fabric_sense.fabric_sense.py.sales_order.send_order_ready_notification",
					args: {
						sales_order: frm.doc.name,
					},
					callback: function (r) {
						if (!r.exc) {
							frappe.msgprint({
								title: __("Success"),
								indicator: "green",
								message: __("Order ready notification sent to customer"),
							});
						}
					},
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

// Child table event handler for Sales Order Item
frappe.ui.form.on("Sales Order Item", {
	item_code: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];

		// Only proceed if item_code is selected and sku field is empty
		if (row.item_code && !row.sku) {
			// Fetch SKU from Item master
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Item",
					fieldname: "custom_sku",
					filters: {
						name: row.item_code,
					},
				},
				callback: function (r) {
					if (r.message && r.message.custom_sku) {
						// Set the SKU value in the child table row
						frappe.model.set_value(cdt, cdn, "custom_sku", r.message.custom_sku);
					}
				},
			});
		}
	},
});

function check_remaining_items_and_show_button(frm) {
	/**
	 * Check if remaining items exist for Material Request creation
	 * and show appropriate button (Material Request or Multi Material Request)
	 */

	// First, ensure all Material Request buttons are removed
	frm.remove_custom_button("Material Request", "Create");
	frm.remove_custom_button("Material Request");
	frm.remove_custom_button("Additional Material Request", "Create");
	frm.remove_custom_button("Additional Material Request");
	frm.remove_custom_button("Multi Material Request", "Create");
	frm.remove_custom_button("Multi Material Request");

	frappe.call({
		method: "fabric_sense.fabric_sense.py.sales_order.check_remaining_items",
		args: {
			sales_order_name: frm.doc.name,
		},
		callback: function (r) {
			if (r.message !== undefined) {
				const has_remaining_items = r.message;

				if (has_remaining_items) {
					// Show Multi Material Request button if remaining items exist
					frm.add_custom_button(
						__("Multi Material Request"),
						function () {
							frappe.call({
								method: "fabric_sense.fabric_sense.py.sales_order.create_multi_material_request",
								args: {
									sales_order: frm.doc.name,
								},
								freeze: true,
								freeze_message: __("Creating Material Requests..."),
								callback: function (r) {
									if (r.message) {
										if (r.message.purchase_mr || r.message.issue_mr) {
											// Navigate to Material Request list
											frappe.set_route("List", "Material Request", {
												custom_sales_order: frm.doc.name,
											});
										} else {
											frappe.msgprint({
												title: __("No Items"),
												indicator: "orange",
												message: __(
													"No items found to create Material Requests."
												),
											});
										}
									}
								},
							});
						},
						__("Create")
					);
				} else {
					// Show regular Material Request button if no remaining items
					frm.add_custom_button(
						__("Additional Material Request"),
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
			}
		},
	});
}

function add_measurement_sheet_connection(frm) {
	// Multiple attempts to find the connections area
	let connectionsArea = $('.form-dashboard[data-doctype="Sales Order"]');

	if (connectionsArea.length === 0) {
		connectionsArea = $(".form-dashboard");
	}

	if (connectionsArea.length === 0) {
		connectionsArea = $('[data-fieldname="connections"] .form-dashboard-wrapper');
	}

	if (connectionsArea.length === 0) {
		// Try to find any dashboard wrapper
		connectionsArea = $(".form-dashboard-wrapper");
	}

	console.log("Connections area found:", connectionsArea.length);

	if (connectionsArea.length === 0) return;

	// Check if we already added the connection
	if (connectionsArea.find(".measurement-sheet-connection").length > 0) return;

	// Create a simple connection section that matches ERPNext style
	const sourceSection = `
		<div class="measurement-sheet-connection" style="margin-bottom: 15px;">
			<div class="form-dashboard-section">
				<div class="section-head">
					<h5 class="uppercase"><b>${__("Source")}</b></h5>
				</div>
				<div class="section-body">
					<div class="document-link" data-doctype="Measurement Sheet">
						<a href="/app/measurement-sheet/${
							frm.doc.measurement_sheet
						}" class="btn-open no-decoration" title="${__("Open Measurement Sheet")}">
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
