import frappe  # type: ignore
from frappe import _  # type: ignore
from frappe.utils import nowdate, getdate # type: ignore


def generate_customer_code(doc, method=None):
    """
    Auto-generate a unique customer code based on Customer Type, Customer Profile, and Year.

    The code format is: <CustomerType_Abbreviation>-<CustomerProfile_Abbreviation>-<Year>-<Counter>
    Example: IND-RET-2025-001 (Individual-Retail-2025-001)

    The counter is globally unique across all customer types and profiles for the current year.
    When a new year starts, the counter resets to 1.

    Args:
        doc (Document): Customer document object
        method (str): Event method name (e.g., 'before_save', 'validate')

    Returns:
        None
    """
    # Check if both Customer Type and Customer Profile have values
    if not doc.customer_type or not doc.get("custom_customer_profile"):
        return

    # Skip if customer code is already set and we're not updating the key fields
    if (
        doc.get("custom_customer_code")
        and not doc.has_value_changed("customer_type")
        and not doc.has_value_changed("custom_customer_profile")
    ):
        return

    # Get abbreviations for Customer Type
    customer_type_abbr = get_abbreviation(doc.customer_type)

    # Get abbreviations for Customer Profile
    customer_profile_abbr = get_abbreviation(doc.get("custom_customer_profile"))

    # Get current year
    current_year = getdate(nowdate()).year

    # Generate base code with year
    base_code = f"{customer_type_abbr}-{customer_profile_abbr}-{current_year}"

    # Find the next available counter for the current year (globally unique)
    counter = get_next_counter_for_year(current_year, doc.name)

    # Generate the final customer code
    customer_code = f"{base_code}-{counter:03d}"

    # Set the generated customer code
    doc.custom_customer_code = customer_code


def get_next_counter_for_year(year, exclude_customer_name=None):
    """
    Get the next available counter value for the given year.
    The counter is globally unique across all customer types and profiles.

    Args:
        year (int): The year for which to get the counter
        exclude_customer_name (str): Customer name to exclude from the search (for updates)

    Returns:
        int: Next available counter value
    """
    # Pattern to match customer codes for the current year
    # Format: XXX-XXX-YYYY-NNN where YYYY is the year and NNN is the counter
    year_pattern = f"%-{year}-%"

    # Get all customer codes for the current year
    filters = {"custom_customer_code": ["like", year_pattern]}

    if exclude_customer_name:
        filters["name"] = ["!=", exclude_customer_name]

    existing_codes = frappe.get_all(
        "Customer",
        filters=filters,
        fields=["custom_customer_code"],
        order_by="custom_customer_code desc",
        limit=1,
    )

    if not existing_codes:
        # No codes exist for this year, start from 1
        return 1

    # Extract the counter from the last code
    # Format: XXX-XXX-YYYY-NNN
    last_code = existing_codes[0].get("custom_customer_code", "")

    try:
        # Split by '-' and get the last part (counter)
        parts = last_code.split("-")
        if len(parts) >= 4:
            last_counter = int(parts[-1])
            return last_counter + 1
    except (ValueError, IndexError):
        pass

    # If we can't parse the last code, start from 1
    return 1


def get_abbreviation(text):
    """
    Generate a 3-letter abbreviation from the given text.

    Args:
        text (str): Text to abbreviate

    Returns:
        str: 3-letter uppercase abbreviation

    Examples:
        - "Individual" -> "IND"
        - "Company" -> "COM"
        - "Retail" -> "RET"
        - "Wholesale" -> "WHO"
        - "Architect/Designer" -> "ARC"
        - "Purchase Manager" -> "PUR"
    """

    # Remove special characters and split by spaces or slashes
    words = text.replace("/", " ").replace("-", " ").split()

    if len(words) == 1:
        # Single word: take first 3 characters
        return text[:3].upper()
    else:
        # Multiple words: take first letter of each word (up to 3)
        abbr = "".join([word[0] for word in words if word])[:3]
        # If abbreviation is less than 3 characters, pad with first word's characters
        if len(abbr) < 3:
            abbr = (abbr + words[0])[:3]
        return abbr.upper()
