# Copyright (c) 2025, innogenio and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from fabric_sense.fabric_sense.doctype.measurement_sheet.measurement_sheet import MeasurementSheet


class TestMeasurementSheet(FrappeTestCase):
	"""Test cases for Measurement Sheet doctype"""
	
	def test_validate_contractor_assignment(self):
		"""Test validation of contractor assignment fields"""
		# This would require creating a test document
		# For now, this is a placeholder
		pass
	
	def test_validate_measurement_details(self):
		"""Test validation of measurement details table"""
		# This would require creating a test document
		pass
	
	def test_calculate_totals(self):
		"""Test calculation of total amount and net amount"""
		# This would require creating a test document
		pass

	def test_notify_assigned_contractor_sends_email(self):
		"""notify_assigned_contractor should send an email to the resolved recipient"""
		doc = MeasurementSheet({
			"doctype": "Measurement Sheet",
			"name": "MS-TEST-1",
			"customer": "Test Customer",
			"project": None,
			"expected_measurement_date": None,
			"assigned_contractor": "EMP-TEST-1",
		})

		# Mock recipient resolver
		doc._get_contractor_email = lambda x: "tailor@example.com"

		# Capture sendmail calls
		sent = {}
		def _mock_sendmail(**kwargs):
			sent.update(kwargs)
		frappe_sendmail_real = frappe.sendmail
		try:
			frappe.sendmail = _mock_sendmail
			doc.notify_assigned_contractor()
			self.assertIn("recipients", sent)
			self.assertIn("subject", sent)
			self.assertEqual(sent["recipients"], ["tailor@example.com"])
		except Exception as e:
			self.fail(f"notify_assigned_contractor raised Exception: {e}")
		finally:
			frappe.sendmail = frappe_sendmail_real

	def test_after_insert_sends_once(self):
		"""after_insert should send email once when assigned_contractor is present"""
		doc = MeasurementSheet({
			"doctype": "Measurement Sheet",
			"name": "MS-INSERT-1",
			"customer": "Test Customer",
			"assigned_contractor": "EMP-TEST-INS",
		})

		# Mock recipient resolver
		doc._get_contractor_email = lambda x: "tailor@example.com"

		calls = {"count": 0}
		def _mock_sendmail(**kwargs):
			calls["count"] += 1
		frappe_sendmail_real = frappe.sendmail
		try:
			frappe.sendmail = _mock_sendmail
			doc.after_insert()
			self.assertEqual(calls["count"], 1)
		finally:
			frappe.sendmail = frappe_sendmail_real

	def test_before_save_only_on_update(self):
		"""before_save should not send on new docs; should send when updating and value changed"""
		doc = MeasurementSheet({
			"doctype": "Measurement Sheet",
			"name": "MS-UPD-1",
			"customer": "Test Customer",
			"assigned_contractor": "EMP-1",
		})

		# New doc simulation
		doc.is_new = lambda: True
		doc.has_value_changed = lambda f: True
		doc._get_contractor_email = lambda x: "tailor@example.com"

		calls = {"count": 0}
		def _mock_sendmail(**kwargs):
			calls["count"] += 1
		frappe_sendmail_real = frappe.sendmail
		try:
			frappe.sendmail = _mock_sendmail
			# Should NOT send because is_new() is True and controller guards updates
			doc.before_save()
			self.assertEqual(calls["count"], 0)

			# Now simulate update
			doc.is_new = lambda: False
			doc.before_save()
			self.assertEqual(calls["count"], 1)
		finally:
			frappe.sendmail = frappe_sendmail_real

	def test_no_duplicate_on_create_flow(self):
		"""Calling after_insert() then before_save() on a new doc should send only once"""
		doc = MeasurementSheet({
			"doctype": "Measurement Sheet",
			"name": "MS-NODUP-1",
			"customer": "Test Customer",
			"assigned_contractor": "EMP-1",
		})

		doc._get_contractor_email = lambda x: "tailor@example.com"
		doc.has_value_changed = lambda f: True
		doc.is_new = lambda: True

		calls = {"count": 0}
		def _mock_sendmail(**kwargs):
			calls["count"] += 1
		frappe_sendmail_real = frappe.sendmail
		try:
			frappe.sendmail = _mock_sendmail
			# Creation flow
			doc.after_insert()  # sends once
			doc.before_save()   # should not send on new due to guard
			self.assertEqual(calls["count"], 1)
		finally:
			frappe.sendmail = frappe_sendmail_real

	def test_before_save_triggers_on_assigned_contractor_change(self):
		"""before_save should send email when assigned_contractor has changed"""
		doc = MeasurementSheet({
			"doctype": "Measurement Sheet",
			"name": "MS-TEST-2",
			"assigned_contractor": "EMP-TEST-2",
			"customer": "Test Customer",
		})

		# Force change detection
		doc.has_value_changed = lambda field: field == "assigned_contractor"
		doc._get_contractor_email = lambda x: "tailor2@example.com"

		calls = {"count": 0}
		def _mock_sendmail(**kwargs):
			calls["count"] += 1
		frappe_sendmail_real = frappe.sendmail
		try:
			frappe.sendmail = _mock_sendmail
			doc.before_save()
			self.assertEqual(calls["count"], 1)
		finally:
			frappe.sendmail = frappe_sendmail_real

