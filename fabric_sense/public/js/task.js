let task_status_before_save = null;
let cached_contractors = null; // Cache contractors for selected service

frappe.ui.form.on("Task", {
	refresh: function (frm) {
		// Make project field read-only if it has a value
		if (frm.fields_dict.project) {
			if (frm.doc.project) {
				frm.set_df_property("project", "read_only", 1);
			} else {
				// Allow editing if project is empty (for manual entry)
				frm.set_df_property("project", "read_only", 0);
			}
		}

		// Check for tailoring sheet field with different possible names
		const possible_field_names = [
			"tailoring_sheet",
			"custom_tailoring_sheet",
			"tailoring_sheet_link",
		];
		for (let field_name of possible_field_names) {
			if (frm.fields_dict[field_name]) {
				// Set up event listener manually if needed
				if (frm.fields_dict[field_name].$input) {
					frm.fields_dict[field_name].$input.on("change", function () {
						handle_tailoring_sheet_change(frm);
					});
				}
			}
		}

		// Store status before any changes
		if (frm.doc.status) {
			task_status_before_save = frm.doc.status;
		} else {
			// For new documents, set to null
			task_status_before_save = null;
		}

		// Set up get_query for assigned contractor field to filter by service
		if (frm.fields_dict.custom_assigned_contractor) {
			// If service is already selected, fetch contractors
			if (frm.doc.custom_service) {
				fetch_and_cache_contractors(frm, frm.doc.custom_service);
			}

			frm.set_query("custom_assigned_contractor", function () {
				return get_contractor_query(frm);
			});
		}

		// Set up get_query for tailoring sheet field to filter by project
		if (frm.fields_dict.custom_tailoring_sheet) {
			frm.set_query("custom_tailoring_sheet", function () {
				return get_tailoring_sheet_query(frm);
			});
		}

		// Auto-prefill tailoring sheet from project for new tasks
		if (frm.doc.__islocal && frm.doc.project && !frm.doc.custom_tailoring_sheet) {
			// Task is new, has project, but no tailoring sheet - fetch latest tailoring sheet
			frappe.call({
				method: "fabric_sense.fabric_sense.py.task.get_latest_tailoring_sheet_for_project",
				args: {
					project: frm.doc.project,
				},
				callback: function (r) {
					if (r.message && frm.fields_dict.custom_tailoring_sheet) {
						frm.set_value("custom_tailoring_sheet", r.message);
					}
				},
			});
		}

		// Remove any existing "Create Stock Entry" buttons
		const pageActions = frm.page.page_actions;
		pageActions.find(".btn-primary").each(function () {
			const btnText = $(this).text().trim();
			if (btnText === "Create Stock Entry") {
				$(this).remove();
			}
		});

		// Add "Create Stock Entry" button for Working status tasks
		if (frm.doc.status === "Working" && !frm.is_new()) {
			// Get tailoring sheet value
			const tailoring_sheet_value =
				frm.doc.custom_tailoring_sheet || frm.doc.tailoring_sheet;

			if (tailoring_sheet_value) {
				// Check for material request items before adding button
				frappe.call({
					method: "fabric_sense.fabric_sense.py.task.get_material_request_items_for_stock_entry",
					args: {
						tailoring_sheet: tailoring_sheet_value,
					},
					callback: function (r) {
						if (r.message) {
							if (r.message.error) {
								// Show error message
								frappe.msgprint({
									title: __("Error"),
									indicator: "red",
									message: __("Error fetching Material Request: {0}", [
										r.message.error,
									]),
								});
							} else if (r.message.items && r.message.items.length > 0) {
								// Check if Material Request is submitted (docstatus = 1)
								if (r.message.docstatus === 1) {
									// Add Create Stock Entry button
									frm.add_custom_button(__("Create Stock Entry"), function () {
										frappe.confirm(
											__("Are you sure you want to create stock entry?"),
											function () {
												// On confirm - create stock entry
												open_stock_entry_form(
													r.message,
													tailoring_sheet_value,frm
												);
											},
											function () {
												// On cancel - do nothing
											}
										);
									})
										.addClass("btn-primary")
										.prependTo(frm.page.page_actions);
								}
							}
						}
					},
					error: function (r) {
						// Handle error silently for button creation
						console.log("Error checking material request for button:", r);
					},
				});
			}
		}
	},

	custom_assigned_contractor: function (frm) {
		// When Contractor is selected, calculate service rate and charges
		calculate_service_rate_and_charges(frm);
	},

	custom_service: function (frm) {
		// When Service is selected, fetch UOM and calculate service rate and charges
		if (frm.doc.custom_service) {
			// Fetch UOM from Services
			fetch_uom_from_service(frm);

			// Fetch and cache contractors for this service
			fetch_and_cache_contractors(frm, frm.doc.custom_service);
		} else {
			// No service selected, clear cache
			cached_contractors = null;
		}

		// Clear assigned contractor when service changes
		if (frm.fields_dict.custom_assigned_contractor) {
			frm.set_value("custom_assigned_contractor", "");
		}

		// Re-apply query filter
		if (frm.fields_dict.custom_assigned_contractor) {
			frm.set_query("custom_assigned_contractor", function () {
				return get_contractor_query(frm);
			});
		}

		calculate_service_rate_and_charges(frm);
	},

	custom_quantity: function (frm) {
		// When Quantity changes, recalculate charges
		calculate_service_rate_and_charges(frm);
	},

	custom_travelling_charge: function (frm) {
		// When Travelling Charge changes, recalculate total
		calculate_service_rate_and_charges(frm);
	},

	status: function (frm) {
		// Track status changes
		if (frm.doc.status) {
			// Status field changed
		}
	},

	custom_tailoring_sheet: function (frm) {
		handle_tailoring_sheet_change(frm);
	},

	project: function (frm) {
		// Make project field read-only once it's set
		if (frm.doc.project && frm.fields_dict.project) {
			frm.set_df_property("project", "read_only", 1);
		}

		// Clear tailoring sheet when project changes and refresh filter
		if (frm.fields_dict.custom_tailoring_sheet) {
			frm.set_value("custom_tailoring_sheet", "");
			frm.set_query("custom_tailoring_sheet", function () {
				return get_tailoring_sheet_query(frm);
			});
		}
	},

	after_save: function (frm) {
		// Check if status changed to Working
		// Handle both: status changed from Open to Working, and new document with Working status
		if (frm.doc.status === "Working") {
			if (
				task_status_before_save === "Open" ||
				task_status_before_save === null ||
				frm.doc.__islocal
			) {
				// Status changed from Open to Working, or new document with Working status
				show_stock_entry_confirmation(frm);
			}
		}

		// Update stored status
		task_status_before_save = frm.doc.status;
	},
});

function show_stock_entry_confirmation(frm) {
	// Check for tailoring sheet in multiple possible field names (check custom_tailoring_sheet first)
	const tailoring_sheet_value = frm.doc.custom_tailoring_sheet || frm.doc.tailoring_sheet;

	// Check prerequisites
	if (!tailoring_sheet_value) {
		// Show detailed error message
		frappe.msgprint({
			title: __("Prerequisite Missing"),
			indicator: "orange",
			message:
				__(
					"Please select a Tailoring Sheet before changing status to Working. Stock Entry form cannot be opened without a Tailoring Sheet."
				) +
				"<br><br>" +
				__("Debug Info:") +
				"<br>" +
				__("custom_tailoring_sheet field: {0}", [
					frm.doc.custom_tailoring_sheet || "empty",
				]) +
				"<br>" +
				__("tailoring_sheet field: {0}", [frm.doc.tailoring_sheet || "empty"]),
		});
		return;
	}

	// Check for existing Material Request (Issue type) for Stock Entry
	frappe.call({
		method: "fabric_sense.fabric_sense.py.task.get_material_request_items_for_stock_entry",
		args: {
			tailoring_sheet: tailoring_sheet_value,
		},
		callback: function (r) {
			if (r.message) {
				if (r.message.error) {
					// Show error message
					frappe.msgprint({
						title: __("Error"),
						indicator: "red",
						message: __("Error fetching Material Request: {0}", [r.message.error]),
					});
				} else if (r.message.items && r.message.items.length > 0) {
					// Check if Material Request is submitted (docstatus = 1)
					if (r.message.docstatus === 1) {
						// Material Request is submitted, show confirmation dialog
						frappe.confirm(
							__(
								"Material items are available for this task. Would you like to create a Stock Entry to issue materials?"
							),
							function () {
								// User confirmed - proceed to Stock Entry creation
								open_stock_entry_form(r.message, tailoring_sheet_value, frm);
							},
							function () {
								// User cancelled - do nothing, task is already saved with Working status
								frappe.show_alert(
									{
										message: __(
											"Task saved successfully. You can create Stock Entry later if needed."
										),
										indicator: "green",
									},
									3
								);
							}
						);
					} else {
						// Material Request exists but is not submitted
						frappe.msgprint({
							title: __("Material Request Not Submitted"),
							indicator: "orange",
							message: __(
								"Material Request {0} exists but is not submitted. Please submit it before creating Stock Entry.",
								[r.message.material_request_name]
							),
						});
					}
				} else {
					// Show toast message if no Material Request found - no confirmation needed
					frappe.show_alert(
						{
							message: __(
								"Task saved successfully. No material request found for this tailoring sheet."
							),
							indicator: "green",
						},
						3
					);
				}
			}
		},
		error: function (r) {
			// Show user-friendly error message
			let error_msg = r.message || "Unknown error";
			if (typeof error_msg === "object" && error_msg.exc_type) {
				error_msg =
					error_msg.exc_type +
					": " +
					(error_msg.exc || error_msg.message || "Unknown error");
			}

			frappe.msgprint({
				title: __("Error"),
				indicator: "red",
				message: __("Error fetching Material Request: {0}", [error_msg]),
			});
		},
	});
}

function fetch_and_cache_contractors(frm, service) {
	// Fetch contractors for the service and cache them
	frappe.call({
		method: "fabric_sense.fabric_sense.py.task.get_contractors_for_service",
		args: {
			service: service,
		},
		callback: function (r) {
			if (r.message) {
				cached_contractors = r.message;
			} else {
				cached_contractors = [];
			}
		},
		error: function (r) {
			cached_contractors = null;
		},
	});
}

function get_contractor_query(frm) {
	// Get query for contractor field based on selected service
	if (frm.doc.custom_service) {
		// Service is selected
		if (
			cached_contractors &&
			Array.isArray(cached_contractors) &&
			cached_contractors.length > 0
		) {
			// We have cached contractors, filter by them
			return {
				filters: {
					name: ["in", cached_contractors],
				},
			};
		} else if (
			cached_contractors &&
			Array.isArray(cached_contractors) &&
			cached_contractors.length === 0
		) {
			// Service selected but no contractors found
			return {
				filters: {
					name: ["in", [""]], // Empty list to show no results
				},
			};
		} else {
			// Service selected but contractors not yet loaded
			// Fetch contractors (async, but we'll return empty for now and let user retry)
			fetch_and_cache_contractors(frm, frm.doc.custom_service);
			// Return empty filter temporarily - user can click the field again after contractors load
			return {
				filters: {
					name: ["in", [""]], // Empty temporarily
				},
			};
		}
	}

	// If no service selected, show all employees (no filter)
	return {};
}

function get_tailoring_sheet_query(frm) {
	// Get query for tailoring sheet field based on selected project
	if (frm.doc.project) {
		// Project is selected, filter tailoring sheets by project
		return {
			filters: {
				project: frm.doc.project,
			},
		};
	}

	// If no project selected, show all tailoring sheets (no filter)
	return {};
}

function handle_tailoring_sheet_change(frm) {
	// Handler for when tailoring sheet is selected
	// No longer fetches contractor from tailoring sheet

	// If service is already set, trigger calculation
	if (frm.doc.custom_service && frm.doc.custom_assigned_contractor) {
		calculate_service_rate_and_charges(frm);
	}
}

function fetch_uom_from_service(frm) {
	// Fetch UOM from Services doctype when service is selected
	if (frm.doc.custom_service) {
		frappe.call({
			method: "fabric_sense.fabric_sense.py.task.get_service_rate_and_calculate_charges",
			args: {
				service: frm.doc.custom_service,
				contractor: frm.doc.custom_assigned_contractor || "",
				quantity: frm.doc.custom_quantity || 1.0,
				travelling_charge: frm.doc.custom_travelling_charge || 0.0,
			},
			callback: function (r) {
				if (r.message && r.message.uom) {
					// Try multiple possible field names for UOM
					const uom_field_names = ["custom_unit", "unit", "custom_uom", "uom"];

					for (let field_name of uom_field_names) {
						if (frm.fields_dict[field_name]) {
							frm.set_value(field_name, r.message.uom);
							break;
						}
					}
				}
			},
		});
	}
}

function calculate_service_rate_and_charges(frm) {
	// Calculate service rate and charges when Service and Contractor are both set
	if (frm.doc.custom_service && frm.doc.custom_assigned_contractor) {
		frappe.call({
			method: "fabric_sense.fabric_sense.py.task.get_service_rate_and_calculate_charges",
			args: {
				service: frm.doc.custom_service,
				contractor: frm.doc.custom_assigned_contractor,
				quantity: frm.doc.custom_quantity || 1.0,
				travelling_charge: frm.doc.custom_travelling_charge || 0.0,
			},
			callback: function (r) {
				if (r.message) {
					// Set calculated values
					if (frm.fields_dict.custom_service_rate) {
						frm.set_value("custom_service_rate", r.message.service_rate);
					}
					if (frm.fields_dict.custom_service_charge) {
						frm.set_value("custom_service_charge", r.message.service_charge);
					}
					if (frm.fields_dict.custom_total_contractor_amount) {
						frm.set_value(
							"custom_total_contractor_amount",
							r.message.total_contractor_amount
						);
					}

					// Set UOM if returned
					if (r.message.uom) {
						const uom_field_names = ["custom_unit", "unit", "custom_uom", "uom"];

						for (let field_name of uom_field_names) {
							if (frm.fields_dict[field_name]) {
								frm.set_value(field_name, r.message.uom);
								break;
							}
						}
					}
				}
			},
		});
	} else {
		// Clear values if Service or Contractor is not set
		if (frm.fields_dict.custom_service_rate) {
			frm.set_value("custom_service_rate", 0.0);
		}
		if (frm.fields_dict.custom_service_charge) {
			frm.set_value("custom_service_charge", 0.0);
		}
		if (frm.fields_dict.custom_total_contractor_amount) {
			frm.set_value("custom_total_contractor_amount", 0.0);
		}
	}
}

function open_stock_entry_form(material_request_data, tailoring_sheet,frm) {
	// Create Stock Entry from Material Request
	if (material_request_data.items && material_request_data.items.length > 0) {
		// Create new Stock Entry document
		frappe.model.with_doctype("Stock Entry", function () {
			let stock_entry = frappe.model.get_new_doc("Stock Entry");

			// Set Stock Entry type to Material Issue
			stock_entry.stock_entry_type = "Material Issue";
			stock_entry.purpose = "Material Issue";
			stock_entry.custom_task = frm.doc.name;
			// stock_entry.material_request = material_request_data.material_request_name;

			// Link Tailoring Sheet to Stock Entry if field exists
			if (tailoring_sheet) {
				// Try to set custom_tailoring_sheet field if it exists
				// Use try-catch since meta might not be available immediately for new docs
				try {
					// Check if meta exists and has the field
					if (stock_entry.meta && typeof stock_entry.meta.has_field === "function") {
						if (stock_entry.meta.has_field("custom_tailoring_sheet")) {
							stock_entry.custom_tailoring_sheet = tailoring_sheet;
						}
					} else {
						// If meta is not available, try setting it directly
						// Frappe will ignore it if the field doesn't exist
						stock_entry.custom_tailoring_sheet = tailoring_sheet;
					}
				} catch (e) {
					// If field doesn't exist or there's an error, just continue
				}
			}

			// Handle multiple Material Requests: use first MR name if comma-separated
			// let primary_mr_name = material_request_data.material_request_name;
			// if (primary_mr_name && primary_mr_name.includes(", ")) {
			// 	// Multiple MRs exist - use first one for linking (Frappe doesn't support multiple MRs in single field)
			// 	primary_mr_name = primary_mr_name.split(", ")[0];
			// }

			// Add items from Material Request (aggregated from potentially multiple MRs)
			material_request_data.items.forEach(function (item, index) {
				let stock_entry_item = frappe.model.add_child(stock_entry, "items");

				// Set item_code first - this will trigger stock_uom population
				stock_entry_item.item_code = item.item_code;

				// Set stock_uom (mandatory field) - use from Material Request or fallback to uom
				stock_entry_item.stock_uom = item.stock_uom || item.uom;

				// Set uom
				stock_entry_item.uom = item.uom;

				// Set conversion_factor (mandatory field)
				// If uom equals stock_uom, conversion_factor is 1
				if (item.uom === item.stock_uom || !item.stock_uom) {
					stock_entry_item.conversion_factor = 1;
				} else {
					// For different UOMs, set to 1 initially - Frappe will recalculate
					stock_entry_item.conversion_factor = 1;
				}

				stock_entry_item.qty = item.qty;
				// Set transfer_qty (Qty as per Stock UOM) to satisfy mandatory field
				// transfer_qty = qty * conversion_factor
				stock_entry_item.transfer_qty =
					item.qty * (stock_entry_item.conversion_factor || 1);
				stock_entry_item.item_name = item.item_name;
				stock_entry_item.description = item.description;
				// stock_entry_item.material_request = primary_mr_name;
				// material_request_item is None when items are aggregated from multiple MRs
				// Only set if item.name exists (single MR scenario)
				// if (item.name) {
				// 	stock_entry_item.material_request_item = item.name;
				// }
			});

			// Refresh fields to trigger calculations and UOM conversions
			// Trigger item_code for each item to ensure stock_uom and conversion_factor are calculated
			stock_entry.items.forEach(function (item) {
				// Trigger item_code field change to populate stock_uom and calculate conversion_factor
				frappe.model.trigger(
					"item_code",
					stock_entry.doctype,
					stock_entry.name,
					item.name
				);
				// Trigger uom field change to recalculate conversion_factor if needed
				frappe.model.trigger("uom", stock_entry.doctype, stock_entry.name, item.name);
				// Ensure transfer_qty is kept in sync (Qty as per Stock UOM)
				if (!item.transfer_qty && item.qty) {
					item.transfer_qty = item.qty * (item.conversion_factor || 1);
				}
			});

			// Refresh the items table
			frappe.model.trigger("items", stock_entry.doctype, stock_entry.name);

			// Navigate to the new Stock Entry form
			frappe.set_route("Form", "Stock Entry", stock_entry.name);

			// Show message after a short delay to ensure form is loaded
			setTimeout(function () {
				frappe.msgprint({
					title: __("Stock Entry Created"),
					indicator: "green",
					message: __(
						"Stock Entry form has been opened with items from Material Request. Please review, set source warehouse, and submit."
					),
				});
			}, 500);
		});
	} else {
		frappe.msgprint({
			title: __("Information"),
			indicator: "blue",
			message: __("No items found in Material Request to create Stock Entry."),
		});
	}
}
