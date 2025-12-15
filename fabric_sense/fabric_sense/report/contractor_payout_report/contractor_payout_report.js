// Copyright (c) 2025, innogenio and contributors
// For license information, please see license.txt

frappe.query_reports["Contractor Payout Report"] = {
	"filters": [
		{
			fieldname: "contractor",
			label: "Contractor",
			fieldtype: "Link",
			options: "Employee"
		},
		{
			fieldname: "payment_date",
			label: "Payment Date",
			fieldtype: "Date Range"
		}
	]
};
