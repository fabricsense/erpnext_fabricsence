// Copyright (c) 2025, innogenio and contributors
// For license information, please see license.txt

frappe.query_reports["Discounts Provided"] = {
	"filters": [
		{
			"fieldname": "Date",
			"label": "Date",
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 0
		},
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
			"reqd": 1
		}
	]
};