# -*- coding: utf-8 -*-
import frappe  # type: ignore
from frappe import _  # type: ignore
from erpnext.stock.doctype.item.item import Item  # type: ignore
import re


class CustomItem(Item):
    def autoname(self):
        """Generate SKU when codes are provided; otherwise fall back to default naming."""
        if self.custom_category_code and self.custom_vendor_code:
            # Validate and clean the codes
            category = self._validate_and_clean_code(
                self.custom_category_code, "Category Code"
            )
            # Extract vendor code part from select field (e.g., "57654DSD - supplier1" -> "57654DSD")
            vendor_code_only = self._extract_vendor_code(self.custom_vendor_code)
            vendor = self._validate_and_clean_code(vendor_code_only, "Vendor Code")

            # Use a SINGLE global series for the running number
            running_number = frappe.model.naming.make_autoname("SKU-.####")
            # Extract just the numeric part (removes "SKU-" prefix)
            sequence = running_number.split("-")[-1]

            # Build final SKU
            self.custom_sku = f"{category}-{vendor}-{sequence}"
            # Let the document use default naming (don't set self.name)
            super().autoname()
            return

        # Use the standard Item autoname when SKU inputs are missing
        super().autoname()

    def _extract_vendor_code(self, vendor_field_value):
        """
        Extract vendor code from select field value.
        Format: "57654DSD - supplier1" -> "57654DSD"
        """
        vendor_str = str(vendor_field_value).strip()
        # Split by " - " and take the first part
        if " - " in vendor_str:
            return vendor_str.split(" - ")[0].strip()
        # If no separator, return the whole value
        return vendor_str

    def _validate_and_clean_code(self, code, field_name):
        """
        Validate code format - reject if contains invalid characters
        Only allows alphanumeric characters (A-Z, 0-9)
        """
        cleaned_code = str(code).strip().upper()

        if not cleaned_code:
            frappe.throw(_("{0} cannot be empty").format(field_name))

        if not re.match(r"^[A-Z0-9]+$", cleaned_code):
            frappe.throw(
                _(
                    "{0} contains invalid characters. "
                    "Only alphanumeric characters (A-Z, 0-9) are allowed. "
                    "Special characters, hyphens, and spaces are not permitted. "
                    "Current value: {1}"
                ).format(field_name, code)
            )

        if len(cleaned_code) > 10:
            frappe.throw(
                _("{0} cannot exceed 10 characters. Current length: {1}").format(
                    field_name, len(cleaned_code)
                )
            )

        return cleaned_code

    def validate(self):
        """Additional validations and SKU regeneration on edit"""
        super().validate()

        # Handle SKU logic for both new and existing items
        if not self.is_new():
            # Check if category or vendor code has changed
            if self.has_value_changed("custom_category_code") or self.has_value_changed(
                "custom_vendor_code"
            ):
                if self.custom_category_code and self.custom_vendor_code:
                    # Both fields present - generate/regenerate SKU
                    category = self._validate_and_clean_code(
                        self.custom_category_code, "Category Code"
                    )
                    vendor_code_only = self._extract_vendor_code(
                        self.custom_vendor_code
                    )
                    vendor = self._validate_and_clean_code(
                        vendor_code_only, "Vendor Code"
                    )

                    # Generate new SKU with global sequence
                    running_number = frappe.model.naming.make_autoname("SKU-.####")
                    sequence = running_number.split("-")[-1]

                    self.custom_sku = f"{category}-{vendor}-{sequence}"
                elif not self.custom_category_code and not self.custom_vendor_code:
                    # Both fields are empty - clear the SKU (for service items)
                    self.custom_sku = None
