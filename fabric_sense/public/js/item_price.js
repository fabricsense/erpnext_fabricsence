frappe.ui.form.on('Item Price', {
    item_code: function(frm) {
        fetch_base_and_compute(frm);
    },
    
    custom_markup_percentage: function(frm) {
        fetch_base_and_compute(frm);
    },
    
    custom_markup_type: function(frm) {
        fetch_base_and_compute(frm);
    },
    
    refresh: function(frm) {
        if (frm.doc.item_code && !frm.doc.price_list_rate) {
            fetch_base_and_compute(frm);
        }
    }
});

function fetch_base_and_compute(frm) {
    if (!frm.doc.item_code) {
        frm.set_value('price_list_rate', 0);
        return;
    }
    
    frappe.db.get_value('Item', frm.doc.item_code, 'custom_base_rate')
        .then(r => {
            const base_rate = r.message?.custom_base_rate || 0;
            compute_rate(frm, base_rate);
        })
        .catch(err => {
            frappe.msgprint({
                title: __('Error'),
                indicator: 'red',
                message: __('Failed to fetch base rate: {0}', [err.message])
            });
            console.error('Error fetching base rate:', err);
        });
}

function compute_rate(frm, custom_base_rate) {
    const base = parseFloat(custom_base_rate) || 0;
    
    if (base < 0) {
        frappe.msgprint(__('Base rate cannot be negative'));
        return;
    }
    
    if (!frm.doc.custom_markup_percentage) {
        frm.set_value('price_list_rate', base);
        return;
    }
    
    const markup_value = parseFloat(frm.doc.custom_markup_percentage) || 0;
    const calc_type = frm.doc.custom_markup_type || 'Multiplier';
    let rate;
    
    if (calc_type === 'Percentage') {
        // Percentage calculation: base + (base * percentage/100)
        if (markup_value < -100) {
            frappe.msgprint(__('Percentage cannot be less than -100%'));
            return;
        }
        rate = base + (base * (markup_value / 100));
        
    } else {
        // Multiplier calculation: base * multiplier
        if (markup_value < 0) {
            frappe.msgprint(__('Multiplier cannot be negative'));
            return;
        }
        rate = base * markup_value;
    }
    
    frm.set_value('price_list_rate', rate);
}