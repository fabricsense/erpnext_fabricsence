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