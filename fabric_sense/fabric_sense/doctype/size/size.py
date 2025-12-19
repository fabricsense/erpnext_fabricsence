# Copyright (c) 2025, innogenio and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document # type: ignore


class Size(Document):
	def autoname(self):
		self.name = f"{self.size}-{self.uom}".upper()
