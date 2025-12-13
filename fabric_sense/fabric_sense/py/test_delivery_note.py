import types

import frappe

from .delivery_note import send_customer_delivery_notification


class DummyDoc:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        # common DN fields used by handler
        self.doctype = kwargs.get("doctype", "Delivery Note")
        self.name = kwargs.get("name", "DN-TEST-0001")
        self.customer = kwargs.get("customer", "CUST-TEST")
        self.posting_date = kwargs.get("posting_date")
        self.items = kwargs.get("items", [])
        self.contact_person = kwargs.get("contact_person")
        self.contact_email = kwargs.get("contact_email")


def _patch_db_get_value(monkeypatch_map):
    """Patch frappe.db.get_value to return values based on (doctype, name, fieldname)."""
    def fake_get_value(doctype, name, fieldname, as_dict=False):
        key = (doctype, name, fieldname if isinstance(fieldname, str) else tuple(fieldname))
        val = monkeypatch_map.get(key)
        if as_dict:
            return val
        return val
    frappe.db.get_value = fake_get_value  # type: ignore


def _patch_get_all(return_rows):
    def fake_get_all(doctype, filters=None, fields=None, limit=None):
        return return_rows
    frappe.get_all = fake_get_all  # type: ignore


def _spy_sendmail(calls):
    def fake_sendmail(**kwargs):
        calls.append(kwargs)
    frappe.sendmail = fake_sendmail  # type: ignore


def _spy_log_error(logs):
    def fake_log_error(message=None, title=None):
        logs.append({"message": message, "title": title})
    frappe.log_error = fake_log_error  # type: ignore


def test_contact_person_priority(monkeypatch=None):
    """If contact_person is set with an email, it should be used over others."""
    # Patches
    db_map = {
        ("Contact", "CONT-1", "email_id"): "person@example.com",
        ("Customer", "CUST-TEST", "customer_name"): "Test Customer",
    }
    _patch_db_get_value(db_map)
    _patch_get_all([])
    sent = []
    _spy_sendmail(sent)
    _spy_log_error([])

    doc = DummyDoc(name="DN-CP-0001", customer="CUST-TEST", posting_date=frappe.utils.nowdate(), contact_person="CONT-1")

    send_customer_delivery_notification(doc, method="on_submit")

    assert len(sent) == 1
    assert sent[0]["recipients"] == ["person@example.com"]
    assert "Delivery Confirmation" in sent[0]["subject"]


def test_fallback_customer_email_when_no_contact_person():
    db_map = {
        ("Customer", "CUST-TEST", "email_id"): "customer@example.com",
        ("Customer", "CUST-TEST", "customer_name"): "Test Customer",
    }
    _patch_db_get_value(db_map)
    _patch_get_all([])
    sent = []
    _spy_sendmail(sent)
    _spy_log_error([])

    doc = DummyDoc(name="DN-CUST-0002", customer="CUST-TEST", posting_date=frappe.utils.nowdate())

    send_customer_delivery_notification(doc, method="on_submit")

    assert len(sent) == 1
    assert sent[0]["recipients"] == ["customer@example.com"]


def test_no_recipient_logs_and_no_send():
    db_map = {
        ("Customer", "CUST-TEST", "email_id"): None,
        ("Customer", "CUST-TEST", "customer_name"): "Test Customer",
    }
    _patch_db_get_value(db_map)
    _patch_get_all([])
    sent = []
    logs = []
    _spy_sendmail(sent)
    _spy_log_error(logs)

    doc = DummyDoc(name="DN-NO-EMAIL", customer="CUST-TEST", posting_date=frappe.utils.nowdate())

    send_customer_delivery_notification(doc, method="on_submit")

    assert len(sent) == 0
    # We log a No recipient warning
    assert any(l.get("title") == "Delivery Note: No recipient" for l in logs)


def test_message_contains_basic_rows():
    db_map = {
        ("Customer", "CUST-TEST", "email_id"): "customer@example.com",
        ("Customer", "CUST-TEST", "customer_name"): "Test Customer",
    }
    _patch_db_get_value(db_map)
    _patch_get_all([])
    sent = []
    _spy_sendmail(sent)
    _spy_log_error([])

    doc = DummyDoc(name="DN-ROWS-0003", customer="CUST-TEST", posting_date=frappe.utils.nowdate())

    send_customer_delivery_notification(doc, method="on_submit")

    assert len(sent) == 1
    msg = sent[0]["message"]
    assert "Delivery Note" in msg
    assert "Delivery Date" in msg
