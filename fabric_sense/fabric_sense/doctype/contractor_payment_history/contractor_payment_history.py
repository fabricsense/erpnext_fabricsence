# Copyright (c) 2025, innogenio and contributors
# For license information, please see license.txt

import frappe  # type: ignore
from frappe.model.document import Document  # type: ignore


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
            "status": ["in", ["Unpaid", "Partially Paid"]],
        },
        fields=[
            "name",
            "task",
            "project",
            "amount",
            "amount_paid",
            "balance",
            "status",
        ],
        order_by="creation desc",
    )

    return records


@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
    """Create Payment Entry from Contractor Payment History"""
    from frappe.model.mapper import get_mapped_doc  # type: ignore

    def set_missing_values(source, target):
        target.payment_type = "Pay"
        target.party_type = "Employee"
        target.party = source.contractor
        target.paid_amount = source.balance
        target.received_amount = source.balance
        target.remarks = (
            f"Payment for Task: {source.task or ''}, Project: {source.project or ''}"
        )
        target.custom_contractor_payment_history = source.name

        # Set naming series - get default series for Payment Entry
        naming_series = frappe.get_meta("Payment Entry").get_field("naming_series")
        if naming_series and naming_series.options:
            # Get the first option as default
            default_series = naming_series.options.split("\n")[0]
            target.naming_series = default_series

        # Set party name from Employee
        if source.contractor:
            party_name = frappe.get_cached_value(
                "Employee", source.contractor, "employee_name"
            )
            if party_name:
                target.party_name = party_name

        # Set default accounts
        company = frappe.defaults.get_user_default("Company")
        target.paid_from = frappe.get_cached_value(
            "Company", company, "default_cash_account"
        )
        target.paid_to = frappe.get_cached_value(
            "Employee", source.contractor, "payroll_payable_account"
        )

        if not target.paid_to:
            # Fallback to default payable account
            target.paid_to = frappe.get_cached_value(
                "Company", company, "default_payable_account"
            )

        # Set account currencies - get from Account doctype
        if target.paid_from:
            target.paid_from_account_currency = frappe.get_cached_value(
                "Account", target.paid_from, "account_currency"
            )
        if target.paid_to:
            target.paid_to_account_currency = frappe.get_cached_value(
                "Account", target.paid_to, "account_currency"
            )

        # Set company currency as default if account currencies not found
        company_currency = frappe.get_cached_value(
            "Company", company, "default_currency"
        )
        if not target.paid_from_account_currency:
            target.paid_from_account_currency = company_currency
        if not target.paid_to_account_currency:
            target.paid_to_account_currency = company_currency

        # Add Payment Reference for Task
        if source.task:
            target.append(
                "custom_task_reference",
                {
                    "type": "Task",
                    "reference_name": source.task,
                    "grand_total": source.balance,
                    "outstanding": 0.00,
                    "allocated": source.balance,
                    "contractor_payment_history": source.name,
                },
            )

    doclist = get_mapped_doc(
        "Contractor Payment History",
        source_name,
        {
            "Contractor Payment History": {
                "doctype": "Payment Entry",
                "field_map": {"contractor": "party", "balance": "paid_amount"},
            }
        },
        target_doc,
        set_missing_values,
    )

    return doclist


@frappe.whitelist()
def make_payment_entry_for_multiple(
    contractor=None,
    record_names=None,
    target_doc=None,
):
    """Create Payment Entry for multiple Contractor Payment History records"""
    from frappe.model.mapper import get_mapped_doc  # type: ignore
    import json

    # Handle both mapper call (with source_name) and direct call (with contractor/record_names)
    if not contractor and not record_names:
        # This is a mapper call, extract args from frappe.form_dict
        args = frappe.form_dict.get("args")
        if args:
            if isinstance(args, str):
                args = json.loads(args)
            contractor = args.get("contractor")
            record_names = args.get("record_names")

    if isinstance(record_names, str):
        record_names = json.loads(record_names)

    if not contractor or not record_names:
        frappe.throw("Contractor and record names are required")

    # Get all records
    records = frappe.get_all(
        "Contractor Payment History",
        filters={"name": ["in", record_names], "contractor": contractor},
        fields=["name", "task", "project", "balance", "contractor"],
    )

    if not records:
        frappe.throw("No valid records found")

    # Use the first record as the source for mapping if not already set
    source_name = record_names[0]

    def set_missing_values(source, target):
        # Calculate total balance from all records
        total_balance = sum(record.balance for record in records)

        target.payment_type = "Pay"
        target.party_type = "Employee"
        target.party = contractor
        target.paid_amount = total_balance
        target.received_amount = total_balance
        target.custom_is_group_payment = 1

        # Create remarks with all tasks/projects
        tasks = [record.task for record in records if record.task]
        projects = [record.project for record in records if record.project]
        target.remarks = f"Payment for {len(records)} record(s). Tasks: {', '.join(set(tasks))}. Projects: {', '.join(set(projects))}"

        # Set naming series - get default series for Payment Entry
        naming_series = frappe.get_meta("Payment Entry").get_field("naming_series")
        if naming_series and naming_series.options:
            # Get the first option as default
            default_series = naming_series.options.split("\n")[0]
            target.naming_series = default_series

        # Set party name from Employee
        if contractor:
            party_name = frappe.get_cached_value(
                "Employee", contractor, "employee_name"
            )
            if party_name:
                target.party_name = party_name

        # Set default accounts
        company = frappe.defaults.get_user_default("Company")
        target.paid_from = frappe.get_cached_value(
            "Company", company, "default_cash_account"
        )
        target.paid_to = frappe.get_cached_value(
            "Employee", contractor, "payroll_payable_account"
        )

        if not target.paid_to:
            # Fallback to default payable account
            target.paid_to = frappe.get_cached_value(
                "Company", company, "default_payable_account"
            )

        # Set account currencies - get from Account doctype
        if target.paid_from:
            target.paid_from_account_currency = frappe.get_cached_value(
                "Account", target.paid_from, "account_currency"
            )
        if target.paid_to:
            target.paid_to_account_currency = frappe.get_cached_value(
                "Account", target.paid_to, "account_currency"
            )

        # Set company currency as default if account currencies not found
        company_currency = frappe.get_cached_value(
            "Company", company, "default_currency"
        )
        if not target.paid_from_account_currency:
            target.paid_from_account_currency = company_currency
        if not target.paid_to_account_currency:
            target.paid_to_account_currency = company_currency

        # Add Payment References for each Task
        for record in records:
            if record.task:
                target.append(
                    "custom_task_reference",
                    {
                        "type": "Task",
                        "reference_name": record.task,
                        "grand_total": record.balance,
                        "outstanding": 0.00,
                        "allocated": record.balance,
                        "contractor_payment_history": record.name,
                    },
                )

    doclist = get_mapped_doc(
        "Contractor Payment History",
        source_name,
        {
            "Contractor Payment History": {
                "doctype": "Payment Entry",
                "field_map": {"contractor": "party"},
            }
        },
        target_doc,
        set_missing_values,
    )

    return doclist
