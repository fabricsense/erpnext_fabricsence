frappe.listview_settings["Contractor Payment History"] = {
	onload: function (listview) {
		// Hide the default 'Add' button
		this.hide_add_button(listview);

		// Add custom button for making payment
		this.add_custom_button(listview);
	},

	add_custom_button: function (listview) {
		listview.page.add_inner_button(__("Make Payment for Contractor"), function () {
			// Create a dialog with contractor field
			let dialog = new frappe.ui.Dialog({
				title: __("Make Payment for Contractor"),
				fields: [
					{
						fieldname: "contractor",
						fieldtype: "Link",
						label: __("Contractor"),
						options: "Employee",
						reqd: 1,
						onchange: function () {
							let contractor = dialog.get_value("contractor");
							if (contractor) {
								// Reset selected total when contractor changes
								dialog.$wrapper
									.find(".selected-balance-total")
									.text(format_currency(0));

								// Fetch unpaid records for the selected contractor
								frappe.call({
									method: "fabric_sense.fabric_sense.doctype.contractor_payment_history.contractor_payment_history.get_unpaid_records_for_contractor",
									args: { contractor: contractor },
									callback: function (r) {
										if (r.message && r.message.length > 0) {
											// Clear and populate the HTML field with records
											let html = frappe.listview_settings[
												"Contractor Payment History"
											].build_unpaid_records_table(r.message, dialog);
											dialog.fields_dict.unpaid_records_html.$wrapper.html(
												html
											);
											dialog.fields_dict.unpaid_records_section.df.hidden = 0;
											dialog.fields_dict.unpaid_records_section.refresh();
										} else {
											dialog.fields_dict.unpaid_records_html.$wrapper.html(
												'<div class="text-muted text-center p-4">' +
													__(
														"No unpaid records found for this contractor."
													) +
													"</div>"
											);
											dialog.fields_dict.unpaid_records_section.df.hidden = 0;
											dialog.fields_dict.unpaid_records_section.refresh();
										}
									},
								});
							} else {
								// Reset selected total when contractor is cleared
								dialog.$wrapper
									.find(".selected-balance-total")
									.text(format_currency(0));
								dialog.fields_dict.unpaid_records_html.$wrapper.html("");
								dialog.fields_dict.unpaid_records_section.df.hidden = 1;
								dialog.fields_dict.unpaid_records_section.refresh();
							}
						},
					},
					{
						fieldname: "unpaid_records_section",
						fieldtype: "Section Break",
						label: __("Unpaid Records"),
						hidden: 1,
					},
					{
						fieldname: "unpaid_records_html",
						fieldtype: "HTML",
					},
				],
				size: "large",
				primary_action_label: __("Proceed to Payment"),
				primary_action: function (values) {
					if (!values.contractor) {
						frappe.msgprint(__("Please select a contractor"));
						return;
					}

					// Get all checked records (scoped to this dialog)
					let checked_records = [];
					dialog.$wrapper.find(".unpaid-record-check:checked").each(function () {
						checked_records.push($(this).data("record"));
					});

					if (checked_records.length === 0) {
						frappe.msgprint(__("Please select at least one record to pay"));
						return;
					}

					dialog.hide();

					// Create Payment Entry using server method
					if (checked_records.length === 1) {
						// For single record, use the standard make_payment_entry method
						frappe.model.open_mapped_doc({
							method: "fabric_sense.fabric_sense.doctype.contractor_payment_history.contractor_payment_history.make_payment_entry",
							source_name: checked_records[0],
						});
					} else {
						// For multiple records, use the make_payment_entry_for_multiple method
						frappe.model.open_mapped_doc({
							method: "fabric_sense.fabric_sense.doctype.contractor_payment_history.contractor_payment_history.make_payment_entry_for_multiple",
							args: {
								contractor: values.contractor,
								record_names: checked_records,
							},
						});
					}
				},
			});
			dialog.show();
		});
	},

	build_unpaid_records_table: function (records, dialog) {
		let html = `
			<div class="unpaid-records-container">
				<div class="d-flex justify-content-end align-items-center mb-3">
					<div class="text-muted">
						${__("Total Records")}: <strong>${records.length}</strong>
					</div>
				</div>
				<table class="table table-bordered table-hover">
					<thead class="thead-light">
						<tr>
							<th style="width: 40px;"></th>
							<th>${__("ID")}</th>
							<th>${__("Task")}</th>
							<th class="text-right">${__("Amount")}</th>
							<th class="text-right">${__("Paid")}</th>
							<th class="text-right">${__("Balance")}</th>
							<th>${__("Status")}</th>
						</tr>
					</thead>
					<tbody>
		`;

		let total_balance = 0;
		records.forEach(function (record) {
			let status_class =
				record.status === "Unpaid" ? "indicator-pill red" : "indicator-pill orange";
			total_balance += record.balance || 0;

			html += `
				<tr>
					<td class="text-center">
						<input type="checkbox" class="unpaid-record-check"
							data-record="${record.name}" 
							data-balance="${record.balance || 0}"
							data-amount="${record.amount || 0}"
							data-task="${record.task || ""}"
							data-project="${record.project || ""}"
							data-status="${record.status || ""}">
					</td>
					<td><a href="/app/contractor-payment-history/${record.name}" target="_blank">${
				record.name
			}</a></td>
					<td>${record.task || "-"}</td>
					<td class="text-right">${format_currency(record.amount || 0)}</td>
					<td class="text-right">${format_currency(record.amount_paid || 0)}</td>
					<td class="text-right"><strong>${format_currency(record.balance || 0)}</strong></td>
					<td><span class="${status_class}">${record.status}</span></td>
				</tr>
			`;
		});

		html += `
					</tbody>
					<tfoot>
						<tr class="font-weight-bold bg-light">
							<td colspan="5" class="text-right">${__("Total Balance")}:</td>
							<td class="text-right">${format_currency(total_balance)}</td>
							<td></td>
						</tr>
					</tfoot>
				</table>
				<div class="selected-total mt-2 text-right text-muted">
					${__("Selected Total")}: <strong class="selected-balance-total">${format_currency(0)}</strong>
				</div>
			</div>
		`;

		// Add event handlers after a short delay, scoped to this dialog
		setTimeout(function () {
			// Handle individual checkboxes within this dialog only
			dialog.$wrapper.find(".unpaid-record-check").on("change", function () {
				frappe.listview_settings["Contractor Payment History"].update_selected_total(
					dialog
				);
			});

			// Initialize selected total to 0 (no checkboxes are selected by default)
			dialog.$wrapper.find(".selected-balance-total").text(format_currency(0));
		}, 100);

		return html;
	},

	update_selected_total: function (dialog) {
		let total = 0;
		// Only select checkboxes within this dialog instance
		dialog.$wrapper.find(".unpaid-record-check:checked").each(function () {
			total += parseFloat($(this).data("balance")) || 0;
		});
		// Only update the total within this dialog instance
		dialog.$wrapper.find(".selected-balance-total").text(format_currency(total));
	},

	hide_add_button: function (listview) {
		// Remove the default 'Add' button
		listview.page.clear_primary_action();

		// Hide the button using CSS if it still appears
		setTimeout(() => {
			$(".page-head").find('[data-label="Add%20Contractor%20Payment%20History"]').hide();
			$(".page-head").find('button:contains("Add Contractor Payment History")').hide();
			$(".primary-action").hide();
		}, 100);
	},

	primary_action: function () {
		// Do nothing to suppress the default 'Add' button behavior
		return false;
	},
};
