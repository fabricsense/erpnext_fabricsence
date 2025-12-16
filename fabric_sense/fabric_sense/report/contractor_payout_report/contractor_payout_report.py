import frappe
from frappe.utils import getdate


def execute(filters=None):
	filters = filters or {}
	columns = _get_columns()
	data = _get_data(filters)
	return columns, data


def _get_columns():
	return [
		{"fieldname": "contractor", "label": "Contractor Name", "fieldtype": "Link", "options": "Employee", "width": 160},
		{"fieldname": "payment_entry", "label": "Payment Entry No", "fieldtype": "Link", "options": "Payment Entry", "width": 150},
		{"fieldname": "payment_date", "label": "Payment Date", "fieldtype": "Date", "width": 110},
		{"fieldname": "paid_amount", "label": "Paid Amount", "fieldtype": "Currency", "width": 120},
		{"fieldname": "amount_to_be_paid", "label": "Amount to be PAID", "fieldtype": "Currency", "width": 140},
		{"fieldname": "payment_mode", "label": "Payment Mode", "fieldtype": "Data", "width": 120},
		{"fieldname": "approved_by", "label": "Approved By", "fieldtype": "Data", "width": 140},
		{"fieldname": "approval_date", "label": "Approval Date", "fieldtype": "Datetime", "width": 150},
		{"fieldname": "created_by", "label": "Created By", "fieldtype": "Data", "width": 140},
		{"fieldname": "remarks", "label": "Remarks", "fieldtype": "Small Text", "width": 200},
	]


def _get_conditions(filters):
	conditions = []
	values = {}

	if filters.get("contractor"):
		conditions.append("cph.contractor = %(contractor)s")
		values["contractor"] = filters["contractor"]

	if filters.get("payment_date"):
		payment_date = filters["payment_date"]
		# Handle Date Range filter - can be list, tuple, or string
		if isinstance(payment_date, (list, tuple)) and len(payment_date) >= 2:
			start_date, end_date = payment_date[0], payment_date[1]
		elif isinstance(payment_date, str):
			# Single date string
			start_date, end_date = payment_date, payment_date
		else:
			start_date, end_date = None, None
		
		if start_date:
			conditions.append("pe.posting_date >= %(start_date)s")
			values["start_date"] = getdate(start_date)
		if end_date:
			conditions.append("pe.posting_date <= %(end_date)s")
			values["end_date"] = getdate(end_date)

	condition_sql = " and ".join(conditions)
	if condition_sql:
		condition_sql = "where " + condition_sql

	return condition_sql, values


def _get_data(filters):
	condition_sql, values = _get_conditions(filters)

	query = f"""
		select
			cph.contractor,
			cph.payment_entry,
			pe.posting_date as payment_date,
			cph.amount_paid as paid_amount,
			cph.amount as amount_to_be_paid,
			pe.mode_of_payment as payment_mode,
			pe.custom_approved_by as approved_by,
			pe.custom_approved_datetime as approval_date,
			pe.owner as created_by,
			pe.remarks
		from `tabContractor Payment History` cph
		left join `tabPayment Entry` pe on pe.name = cph.payment_entry
		{condition_sql}
		order by pe.posting_date desc, cph.payment_entry
	"""

	return frappe.db.sql(query, values, as_dict=True)
