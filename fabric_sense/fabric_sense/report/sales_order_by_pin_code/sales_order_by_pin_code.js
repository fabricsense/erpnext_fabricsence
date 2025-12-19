// Copyright (c) 2025, innogenio and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Order by Pin Code"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(),
			"reqd": 1
		},
		{
			"fieldname": "pincode",
			"label": "Pin Code",
			"fieldtype": "Data",
			"reqd": 0
		},
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
			"reqd": 0
		},
		{
			"fieldname": "sales_person",
			"label": "Sales Person",
			"fieldtype": "Link",
			"options": "Sales Person",
			"reqd": 0
		},
		{
			"fieldname": "status",
			"label": "Sales Order Status",
			"fieldtype": "MultiSelectList",
			"get_data": function(txt) {
				return [
					{"value": "Draft"},
					{"value": "Approved"},
					{"value": "Completed"},
					{"value": "Cancelled"}
				];
			},
			"reqd": 0
		}
	]
};
