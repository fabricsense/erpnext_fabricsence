# Copyright (c) 2025, innogenio and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "posting_date",
            "label": "Date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "name",
            "label": "Payment Entry",
            "fieldtype": "Link",
            "options": "Payment Entry",
            "width": 150
        },
        {
            "fieldname": "party",
            "label": "Customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150
        },
        {
			"fieldname": "owner",
			"label": "Created By",
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		},
        {
            "fieldname": "total_grand_total",
            "label": "Invoice Grand Total",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "total_outstanding",
            "label": "Invoice Outstanding",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "discount_amount",
            "label": "Discount Amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "paid_amount",
            "label": "Paid Amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
			"fieldname": "remarks",
			"label": "Remarks",
			"fieldtype": "Text",
			"width": 200
		},
    ]

def get_data(filters):
    conditions = []
    
    # Date filter (optional)
    if filters.get("Date"):
        conditions.append(f"pe.posting_date = '{filters.get('Date')}'")
    
    # Customer filter
    if filters.get("customer"):
        conditions.append(f"pe.party = '{filters.get('customer')}'")
    
    # Party type must be Customer
    conditions.append("pe.party_type = 'Customer'")

    # Only submitted records
    conditions.append("pe.docstatus = 1")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    data = frappe.db.sql(f"""
        SELECT 
            pe.posting_date,
            pe.name,
            pe.party,
            pe.party_name,
            pe.paid_amount,
            pe.owner,
            pe.remarks,
            SUM(ped.amount) as discount_amount,
            SUM(per.total_amount) as total_grand_total,
            SUM(per.outstanding_amount) as total_outstanding
        FROM `tabPayment Entry` pe
        LEFT JOIN `tabPayment Entry Deduction` ped ON ped.parent = pe.name
        LEFT JOIN `tabPayment Entry Reference` per ON per.parent = pe.name
        WHERE {where_clause}
        GROUP BY pe.name
        ORDER BY pe.posting_date DESC
    """, as_dict=1)
    
    return data
