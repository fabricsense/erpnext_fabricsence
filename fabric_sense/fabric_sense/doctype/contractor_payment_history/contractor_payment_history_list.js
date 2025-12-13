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
						reqd: 1
					}
				],
				primary_action_label: __('Submit'),
				primary_action: function(values) {
					// Handle the submission here
					frappe.msgprint(__('Selected Contractor: {0}', [values.contractor]));
					dialog.hide();
				}
			});
			dialog.show();
		});
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
