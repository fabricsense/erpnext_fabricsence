# Copyright (c) 2025, innogenio and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "sales_order",
			"label": _("Sales Order No"),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 150
		},
		{
			"fieldname": "order_date",
			"label": _("Order Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "customer_name",
			"label": _("Customer Name"),
			"fieldtype": "Data",
			"width": 180
		},
		{
			"fieldname": "sales_person",
			"label": _("Sales Person"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "pincode",
			"label": _("Pin Code"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "locality",
			"label": _("Area / Locality"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "city",
			"label": _("City"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "state",
			"label": _("State"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "grand_total",
			"label": _("Grand Total"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Sales Order Status"),
			"fieldtype": "Data",
			"width": 130
		}
	]

def get_data(filters):
	"""Fetch data based on filters"""
	conditions = get_conditions(filters)
	
	query = """
		SELECT
			so.name as sales_order,
			so.transaction_date as order_date,
			so.customer_name,
			(SELECT GROUP_CONCAT(DISTINCT sales_person SEPARATOR ', ') 
			 FROM `tabSales Team` 
			 WHERE parent = so.name) as sales_person,
			addr.pincode,
			addr.address_line2 as locality,
			addr.city,
			addr.state,
			so.grand_total,
			so.status
		FROM
			`tabSales Order` so
		LEFT JOIN
			`tabAddress` addr ON so.dispatch_address_name = addr.name
		WHERE
			so.docstatus < 2
			AND so.transaction_date BETWEEN %(from_date)s AND %(to_date)s
			{conditions}
		ORDER BY
			so.transaction_date DESC, addr.pincode
	""".format(conditions=conditions)
	
	data = frappe.db.sql(query, filters, as_dict=1)
	return data


def get_conditions(filters):
	"""Build WHERE conditions from filters"""
	conditions = []
	
	if filters.get("pincode"):
		conditions.append("addr.pincode = %(pincode)s")
	
	if filters.get("customer"):
		conditions.append("so.customer = %(customer)s")
	
	if filters.get("sales_person"):
		conditions.append("""
			EXISTS (
				SELECT 1 FROM `tabSales Team` 
				WHERE parent = so.name 
				AND sales_person = %(sales_person)s
			)
		""")
	
	if filters.get("status"):
		status_list = filters.get("status")
		if isinstance(status_list, str):
			status_list = [status_list]
		if status_list:
			status_conditions = " OR ".join([f"so.status = '{status}'" for status in status_list])
			conditions.append(f"({status_conditions})")
	
	return " AND " + " AND ".join(conditions) if conditions else ""