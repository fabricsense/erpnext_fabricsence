frappe.listview_settings["Contractor Payment History"] = {
	onload: function (listview) {
		// Hide the default 'Add' button
		this.hide_add_button(listview);

		// Add custom button for making payment
		this.add_custom_button(listview);
	},

	add_custom_button: function(listview) {
		listview.page.add_inner_button(__('Make Payment for Contractor'), function() {
			// Create a dialog with contractor field
			let dialog = new frappe.ui.Dialog({
				title: __('Make Payment for Contractor'),
				fields: [
					{
						fieldname: 'contractor',
						fieldtype: 'Link',
						label: __('Contractor'),
						options: 'Employee',
						reqd: 1,
						onchange: function() {
							let contractor = dialog.get_value('contractor');
							if (contractor) {
								// Fetch unpaid records for the selected contractor
								frappe.call({
									method: 'fabric_sense.fabric_sense.doctype.contractor_payment_history.contractor_payment_history.get_unpaid_records_for_contractor',
									args: { contractor: contractor },
									callback: function(r) {
										if (r.message && r.message.length > 0) {
											// Clear and populate the HTML field with records
											let html = frappe.listview_settings["Contractor Payment History"].build_unpaid_records_table(r.message);
											dialog.fields_dict.unpaid_records_html.$wrapper.html(html);
											dialog.fields_dict.unpaid_records_section.df.hidden = 0;
											dialog.fields_dict.unpaid_records_section.refresh();
										} else {
											dialog.fields_dict.unpaid_records_html.$wrapper.html(
												'<div class="text-muted text-center p-4">' + __('No unpaid records found for this contractor.') + '</div>'
											);
											dialog.fields_dict.unpaid_records_section.df.hidden = 0;
											dialog.fields_dict.unpaid_records_section.refresh();
										}
									}
								});
							} else {
								dialog.fields_dict.unpaid_records_html.$wrapper.html('');
								dialog.fields_dict.unpaid_records_section.df.hidden = 1;
								dialog.fields_dict.unpaid_records_section.refresh();
							}
						}
					},
					{
						fieldname: 'unpaid_records_section',
						fieldtype: 'Section Break',
						label: __('Unpaid Records'),
						hidden: 1
					},
					{
						fieldname: 'unpaid_records_html',
						fieldtype: 'HTML'
					}
				],
				size: 'large',
				primary_action_label: __('Proceed to Payment'),
				primary_action: function(values) {
					if (!values.contractor) {
						frappe.msgprint(__('Please select a contractor'));
						return;
					}
					
					// Get all checked records
					let checked_records = [];
					dialog.$wrapper.find('.unpaid-record-check:checked').each(function() {
						checked_records.push($(this).data('record'));
					});
					
					if (checked_records.length === 0) {
						frappe.msgprint(__('Please select at least one record to pay'));
						return;
					}
					
					// Calculate total balance from selected records
					let total_balance = 0;
					checked_records.forEach(function(record_name) {
						let balance = parseFloat(dialog.$wrapper.find('.unpaid-record-check[data-record="' + record_name + '"]').data('balance')) || 0;
						total_balance += balance;
					});
					
					dialog.hide();
					
					// Gather record details for child table
					let record_details = [];
					checked_records.forEach(function(record_name) {
						let $checkbox = dialog.$wrapper.find('.unpaid-record-check[data-record="' + record_name + '"]');
						record_details.push({
							name: record_name,
							balance: parseFloat($checkbox.data('balance')) || 0,
							amount: parseFloat($checkbox.data('amount')) || 0,
							task: $checkbox.data('task') || '',
							project: $checkbox.data('project') || '',
							status: $checkbox.data('status') || ''
						});
					});
					
					// Create Payment Entry with selected records
					frappe.model.with_doctype("Payment Entry", function() {
						let payment_doc = frappe.model.get_new_doc("Payment Entry");
						
						payment_doc.payment_type = "Pay";
						payment_doc.party_type = "Employee";
						payment_doc.party = values.contractor;
						payment_doc.paid_amount = total_balance;
						payment_doc.received_amount = total_balance;
						payment_doc.remarks = "Payment for " + checked_records.length + " record(s): " + checked_records.join(", ");
						
						// Store in sessionStorage for payment_entry.js to pick up
						sessionStorage.setItem("force_party_type_employee", "1");
						sessionStorage.setItem("contractor_party", values.contractor);
						sessionStorage.setItem("contractor_balance", total_balance);
						sessionStorage.setItem("contractor_payment_records", JSON.stringify(record_details));
						
						frappe.set_route("Form", "Payment Entry", payment_doc.name);
					});
				}
			});
			dialog.show();
		});
	},

	build_unpaid_records_table: function(records) {
		let html = `
			<div class="unpaid-records-container">
				<div class="d-flex justify-content-end align-items-center mb-3">
					<div class="text-muted">
						${__('Total Records')}: <strong>${records.length}</strong>
					</div>
				</div>
				<table class="table table-bordered table-hover">
					<thead class="thead-light">
						<tr>
							<th style="width: 40px;"></th>
							<th>${__('ID')}</th>
							<th>${__('Task')}</th>
							<th>${__('Project')}</th>
							<th class="text-right">${__('Amount')}</th>
							<th class="text-right">${__('Paid')}</th>
							<th class="text-right">${__('Balance')}</th>
							<th>${__('Status')}</th>
						</tr>
					</thead>
					<tbody>
		`;
		
		let total_balance = 0;
		records.forEach(function(record) {
			let status_class = record.status === 'Unpaid' ? 'indicator-pill red' : 'indicator-pill orange';
			total_balance += record.balance || 0;
			
			html += `
				<tr>
					<td class="text-center">
						<input type="checkbox" class="unpaid-record-check" 
							data-record="${record.name}" 
							data-balance="${record.balance || 0}"
							data-amount="${record.amount || 0}"
							data-task="${record.task || ''}"
							data-project="${record.project || ''}"
							data-status="${record.status || ''}">
					</td>
					<td><a href="/app/contractor-payment-history/${record.name}" target="_blank">${record.name}</a></td>
					<td>${record.task || '-'}</td>
					<td>${record.project || '-'}</td>
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
							<td colspan="6" class="text-right">${__('Total Balance')}:</td>
							<td class="text-right">${format_currency(total_balance)}</td>
							<td></td>
						</tr>
					</tfoot>
				</table>
				<div class="selected-total mt-2 text-right text-muted">
					${__('Selected Total')}: <strong class="selected-balance-total">0.00</strong>
				</div>
			</div>
		`;
		
		// Add event handlers after a short delay
		setTimeout(function() {
			// Handle individual checkboxes
			$('.unpaid-record-check').on('change', function() {
				frappe.listview_settings["Contractor Payment History"].update_selected_total();
			});
		}, 100);
		
		return html;
	},

	update_selected_total: function() {
		let total = 0;
		$('.unpaid-record-check:checked').each(function() {
			total += parseFloat($(this).data('balance')) || 0;
		});
		$('.selected-balance-total').text(format_currency(total));
	},
    
	hide_add_button: function(listview) {
		// Remove the default 'Add' button
		listview.page.clear_primary_action();
		
		// Hide the button using CSS if it still appears
		setTimeout(() => {
			$('.page-head').find('[data-label="Add%20Contractor%20Payment%20History"]').hide();
			$('.page-head').find('button:contains("Add Contractor Payment History")').hide();
			$('.primary-action').hide();
		}, 100);
	},

	primary_action: function () {
		// Do nothing to suppress the default 'Add' button behavior
		return false;
	},
};
