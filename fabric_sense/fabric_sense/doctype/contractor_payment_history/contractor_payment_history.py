# Copyright (c) 2025, innogenio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ContractorPaymentHistory(Document):
	def before_save(self):
		"""Calculate balance before saving the document."""
		self.calculate_balance()
	
	def calculate_balance(self):
		"""Calculate balance as Amount Due to the Contractor - Amount Paid."""
		if self.amount and self.amount_paid:
			self.balance = self.amount - self.amount_paid
		elif self.amount:
			self.balance = self.amount
		else:
			self.balance = 0


@frappe.whitelist()
def get_unpaid_records_for_contractor(contractor):
	"""Get all unpaid Contractor Payment History records for a specific contractor."""
	if not contractor:
		return []
	
	records = frappe.get_all(
		"Contractor Payment History",
		filters={
			"contractor": contractor,
			"status": ["in", ["Unpaid", "Partially Paid"]]
		},
		fields=["name", "task", "project", "amount", "amount_paid", "balance", "status"],
		order_by="creation desc"
	)
	
	return records
