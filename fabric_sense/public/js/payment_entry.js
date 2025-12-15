frappe.ui.form.on("Payment Entry", {
	setup: function(frm) {
		// Check sessionStorage flag
		let forceEmployee = sessionStorage.getItem("force_party_type_employee");
		
		// Setup runs first - force party_type if coming from Contractor Payment History
		if (forceEmployee === "1" || frm.doc.custom_contractor_payment_history) {
			frm.doc.party_type = "Employee";
			
			// Try to set party from sessionStorage
			let contractorParty = sessionStorage.getItem("contractor_party");
			if (contractorParty && !frm.doc.party) {
				frm.doc.party = contractorParty;
			}
		}
	},
	
	onload: function (frm) {
		// Check sessionStorage flags
		let forceEmployee = sessionStorage.getItem("force_party_type_employee");
		let contractorRef = sessionStorage.getItem("contractor_payment_ref");
		let contractorParty = sessionStorage.getItem("contractor_party");
		let contractorBalance = sessionStorage.getItem("contractor_balance");
		let contractorPaymentRecords = sessionStorage.getItem("contractor_payment_records");
		
		// Force party_type to Employee if created from Contractor Payment History
		if (frm.is_new() && (forceEmployee === "1" || frm.doc.custom_contractor_payment_history)) {
			// Override party_type immediately and repeatedly
			frm.doc.party_type = "Employee";
			frm.set_value("party_type", "Employee");
			
			// Set party from sessionStorage immediately
			if (contractorParty) {
				frm.doc.party = contractorParty;
				
				// Also set it with a delay to ensure it sticks
				setTimeout(function() {
					frm.set_value("party", contractorParty);
				}, 100);
				
				setTimeout(function() {
					if (!frm.doc.party || frm.doc.party !== contractorParty) {
						frm.set_value("party", contractorParty);
					}
				}, 300);
			}
			
			// Store contractor payment records in JSON field
			if (contractorPaymentRecords) {
				try {
					let records = JSON.parse(contractorPaymentRecords);
					if (records && records.length > 0) {
						// Store the JSON directly in the Long Text field
						frm.doc.custom_contractor_payment_records_json = contractorPaymentRecords;
						
						// Set the first record as the main reference (for backward compatibility)
						frm.set_value("custom_contractor_payment_history", records[0].name);
						
						// Also set it with a delay to ensure it persists
						setTimeout(function() {
							frm.set_value("custom_contractor_payment_records_json", contractorPaymentRecords);
						}, 200);
					}
				} catch (e) {
					console.error("Error parsing contractor payment records:", e);
				}
			}
			
			// Set the first account in Account Paid From field
			setTimeout(function() {
				if (!frm.doc.paid_from) {
					frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "Account",
							filters: {
								account_type: ["in", ["Bank", "Cash"]],
								is_group: 0,
								company: frm.doc.company || frappe.defaults.get_user_default("Company")
							},
							fields: ["name"],
							limit: 1,
							order_by: "name asc"
						},
						callback: function(r) {
							if (r.message && r.message.length > 0) {
								frm.set_value("paid_from", r.message[0].name);
							}
						}
					});
				}
			}, 400);
			
			// Get contractor payment history details (for single record case)
			let cph_ref = frm.doc.custom_contractor_payment_history || contractorRef;
			
			if (cph_ref && !contractorPaymentRecords) {
				frappe.call({
					method: "frappe.client.get",
					args: {
						doctype: "Contractor Payment History",
						name: cph_ref
					},
					callback: function(r) {
						if (r.message) {
							// Force party_type again before setting party
							frm.doc.party_type = "Employee";
							frm.set_value("party_type", "Employee");
							
							// Set party (contractor) if not already set
							if (!frm.doc.party && r.message.contractor) {
								setTimeout(function() {
									frm.set_value("party", r.message.contractor);
								}, 100);
							}
						}
					}
				});
			}
			
			// Clear sessionStorage after use
			setTimeout(function() {
				sessionStorage.removeItem("force_party_type_employee");
				sessionStorage.removeItem("contractor_payment_ref");
				sessionStorage.removeItem("contractor_party");
				sessionStorage.removeItem("contractor_balance");
				sessionStorage.removeItem("contractor_task");
				sessionStorage.removeItem("contractor_project");
				sessionStorage.removeItem("contractor_payment_records");
			}, 1000);
		}
	},
	
	refresh: function (frm) {
		// Force party_type to Employee if custom_contractor_payment_history is set
		if (frm.is_new() && frm.doc.custom_contractor_payment_history) {
			// Aggressively set party_type to Employee
			if (frm.doc.party_type !== "Employee") {
				frm.doc.party_type = "Employee";
				frm.refresh_field("party_type");
			}
			
			// Use multiple approaches to ensure it sticks
			setTimeout(function() {
				if (frm.doc.party_type !== "Employee") {
					frm.doc.party_type = "Employee";
					frm.refresh_field("party_type");
					
					// Try setting through the field object directly
					let field = frm.fields_dict.party_type;
					if (field && field.set_value) {
						field.set_value("Employee");
					}
				}
				
				// Ensure party is set if it's empty
				if (!frm.doc.party && frm.doc.custom_contractor_payment_history) {
					frappe.db.get_value("Contractor Payment History", frm.doc.custom_contractor_payment_history, "contractor")
						.then(r => {
							if (r.message && r.message.contractor) {
								frm.set_value("party", r.message.contractor);
							}
						});
				}
			}, 50);
			
			setTimeout(function() {
				if (frm.doc.party_type !== "Employee") {
					frm.doc.party_type = "Employee";
					frm.refresh_field("party_type");
				}
			}, 200);
			
			setTimeout(function() {
				if (frm.doc.party_type !== "Employee") {
					frm.doc.party_type = "Employee";
					frm.refresh_field("party_type");
				}
			}, 500);
		}
		
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
	party_type: function(frm) {
		// Lock party_type to Employee if linked to Contractor Payment History
		if (frm.doc.custom_contractor_payment_history && frm.doc.party_type !== "Employee") {
			frm.set_value("party_type", "Employee");
			frappe.show_alert({
				message: __("Party Type must be Employee for Contractor Payments"),
				indicator: "orange"
			});
		}
		
		// When party_type is set to Employee from Contractor Payment History, set the party
		if (frm.is_new() && frm.doc.party_type === "Employee" && frm.doc.custom_contractor_payment_history && !frm.doc.party) {
			// Try to get party from sessionStorage first
			let contractorParty = sessionStorage.getItem("contractor_party");
			if (contractorParty) {
				setTimeout(function() {
					frm.set_value("party", contractorParty);
				}, 50);
			} else {
				// Fetch from database
				frappe.db.get_value("Contractor Payment History", frm.doc.custom_contractor_payment_history, "contractor")
					.then(r => {
						if (r.message && r.message.contractor) {
							setTimeout(function() {
								frm.set_value("party", r.message.contractor);
							}, 50);
						}
					});
			}
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
