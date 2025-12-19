frappe.ui.form.on("Payment Entry", {
	refresh: function (frm) {
		// Handle auto-filling from Contractor Payment History
		if (
			(frm.doc.custom_contractor_payment_history || frm.doc.custom_is_group_payment) &&
			frm.doc.party_type === "Employee"
		) {
			// Ensure the form is properly set up for contractor payments
			frm.set_df_property("party_type", "read_only", 1);
			frm.set_df_property("party", "read_only", 1);
		}

		// Ensure Save button is visible for new documents
		if (frm.is_new()) {
			// Force show the save button if it's missing
			setTimeout(() => {
				if (!frm.page.btn_primary || frm.page.btn_primary.is(':hidden')) {
					frm.page.set_primary_action(__('Save'), function() {
						frm.save();
					}, 'fa fa-floppy-o');
				}
			}, 100);
		}

		// Set custom filter for paid_to field when payment type is Pay and party type is Employee
		set_paid_to_account_filter(frm);

		// Remove existing custom buttons to prevent duplicates
		// Only remove custom buttons, not standard ERPNext buttons like Save
		const pageActions = frm.page.page_actions;
		pageActions.find(".btn-custom").each(function () {
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
								fieldname: {
									custom_manager_approval_status: "Discount Approved",
									custom_discount_approved_by:
										frappe.session.user_fullname || frappe.session.user,
									custom_discound_approved_datetime:
										frappe.datetime.now_datetime(),
								},
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
				.addClass("btn-primary btn-custom")
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
				.addClass("btn-primary btn-custom")
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
								fieldname: {
									custom_manager_approval_status: "Approved",
									custom_approved_by:
										frappe.session.user_fullname || frappe.session.user,
									custom_approved_datetime: frappe.datetime.now_datetime(),
								},
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
				.addClass("btn-primary btn-custom")
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
				.addClass("btn-primary btn-custom")
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
				.addClass("btn-primary btn-custom")
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
				.addClass("btn-primary btn-custom")
				.prependTo(frm.page.page_actions);
		}
	},

	payment_type: function (frm) {
		// Update paid_to account filter when payment type changes
		set_paid_to_account_filter(frm);
	},

	party_type: function (frm) {
		// Update paid_to account filter when party type changes
		set_paid_to_account_filter(frm);
	},

	party: function (frm) {
		// Update paid_to account filter when party changes
		set_paid_to_account_filter(frm);
	},

	paid_amount: function (frm) {
		// Auto-distribute paid amount across tasks when paid_amount changes
		distribute_paid_amount_across_tasks(frm);
	},
});

// Function to distribute paid amount proportionally across tasks
function distribute_paid_amount_across_tasks(frm) {
	// Skip if we're already in the middle of distributing amounts to prevent loops
	if (frm._distributing_amounts) {
		return;
	}

	// Skip if no custom_task_reference table or if it's empty
	if (!frm.doc.custom_task_reference || frm.doc.custom_task_reference.length === 0) {
		return;
	}

	// Skip if paid_amount is not set or is zero
	let paid_amount = flt(frm.doc.paid_amount);
	if (paid_amount <= 0) {
		return;
	}

	// Set flag to prevent loops
	frm._distributing_amounts = true;

	// Calculate total grand_total from all tasks
	let total_grand_total = 0;
	frm.doc.custom_task_reference.forEach(function (row) {
		total_grand_total += flt(row.grand_total);
	});

	// Skip if total grand total is zero to avoid division by zero
	if (total_grand_total <= 0) {
		frm._distributing_amounts = false;
		return;
	}

	// Distribute paid amount sequentially task by task
	let remaining_amount = paid_amount;

	frm.doc.custom_task_reference.forEach(function (row, index) {
		let allocated_amount = 0;
		let task_grand_total = flt(row.grand_total);

		if (remaining_amount > 0) {
			if (remaining_amount >= task_grand_total) {
				// Fully allocate this task's grand total
				allocated_amount = task_grand_total;
				remaining_amount -= task_grand_total;
			} else {
				// Partially allocate remaining amount to this task
				allocated_amount = remaining_amount;
				remaining_amount = 0;
			}
		}

		// Update the allocated amount for this row
		frappe.model.set_value(row.doctype, row.name, "allocated", allocated_amount);

		// Calculate and update outstanding amount
		let outstanding = task_grand_total - allocated_amount;
		frappe.model.set_value(row.doctype, row.name, "outstanding", outstanding);
	});

	// Refresh the child table to show updated values
	frm.refresh_field("custom_task_reference");

	// Clear the flag after a short delay
	setTimeout(() => {
		frm._distributing_amounts = false;
	}, 100);
}

// Function to calculate total paid amount from all reference tables
function calculate_total_paid_amount(frm) {
	let total_allocated = 0;

	// Calculate from custom_task_reference table
	if (frm.doc.custom_task_reference && frm.doc.custom_task_reference.length > 0) {
		frm.doc.custom_task_reference.forEach(function (row) {
			if (row.allocated) {
				total_allocated += flt(row.allocated);
			}
		});
	}

	// Only update if there's a change to avoid unnecessary triggers
	// Also check if we're not in the middle of distributing amounts to prevent loops
	if (flt(frm.doc.paid_amount) !== total_allocated && !frm._distributing_amounts) {
		// Set flag to prevent infinite loops during distribution
		frm._distributing_amounts = true;

		frm.set_value("paid_amount", total_allocated);

		// For outgoing payments (Pay), also update received_amount
		if (frm.doc.payment_type === "Pay") {
			frm.set_value("received_amount", total_allocated);
		}

		// Clear the flag after a short delay
		setTimeout(() => {
			frm._distributing_amounts = false;
		}, 100);
	}
}

// Handle Custom Task Reference child table
frappe.ui.form.on("Task Payment Reference", {
	allocated: function (frm, cdt, cdn) {
		calculate_outstanding(cdt, cdn);
		calculate_total_paid_amount(frm);
	},
	grand_total: function (frm, cdt, cdn) {
		calculate_outstanding(cdt, cdn);
	},
	custom_task_reference_remove: function (frm) {
		calculate_total_paid_amount(frm);
	},
});

// Function to calculate outstanding amount for Task Payment Reference
function calculate_outstanding(cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.grand_total !== undefined && row.allocated !== undefined) {
		let outstanding = flt(row.grand_total) - flt(row.allocated);
		frappe.model.set_value(cdt, cdn, "outstanding", outstanding);
	}
}

// Function to set custom filter for paid_to account field
function set_paid_to_account_filter(frm) {
	// Only apply custom filter when payment type is "Pay" and party type is "Employee"
	if (frm.doc.payment_type === "Pay" && frm.doc.party_type === "Employee" && frm.doc.party) {
		// Set custom filter to include both Payable and Expense Account types
		frm.set_query("paid_to", function() {
			return {
				"filters": [
					["Account", "account_type", "in", ["Payable", "Expense Account"]],
					["Account", "is_group", "=", 0],
					["Account", "company", "=", frm.doc.company]
				]
			};
		});
	} else {
		// Clear custom filter for other scenarios - let ERPNext handle default filters
		frm.set_query("paid_to", function() {
			return {};
		});
	}
}
