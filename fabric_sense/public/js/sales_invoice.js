frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        // Show "Send Order Ready Notification" button
        if (frm.doc.docstatus === 1 && !frm.doc.order_ready_notification_sent) {
            frm.add_custom_button(__('Send Order Ready Notification'), function() {
                frappe.call({
                    method: 'fabric_sense.fabric_sense.py.sales_invoice_notifications.send_order_ready_notification',
                    args: {
                        sales_invoice_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__('Order Ready Notification sent successfully'));
                            frm.reload_doc();
                        }
                    }
                });
            }, __('Notifications'));
        }
    }
});

// Child table event handler for Sales Invoice Item
frappe.ui.form.on("Sales Invoice Item", {
	item_code: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];

		// Only proceed if item_code is selected and sku field is empty
		if (row.item_code && !row.custom_sku) {
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