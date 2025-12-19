# Copyright (c) 2025, innogenio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Brands(Document):
	pass


@frappe.whitelist()
def get_brands_by_item_group(doctype, txt, searchfield, start, page_len, filters):
	"""
	Custom query function to filter brands based on item group.
	Returns brands that have the specified item group in their sub_categories child table.
	"""
	item_group = filters.get("item_group")
	
	if not item_group:
		# If no item group is specified, return all brands
		return frappe.db.sql("""
			SELECT name, brand_name
			FROM `tabBrands`
			WHERE name LIKE %(txt)s
			ORDER BY brand_name
			LIMIT %(start)s, %(page_len)s
		""", {
			"txt": "%" + txt + "%",
			"start": start,
			"page_len": page_len
		})
	
	# Filter brands that have the specified item group in their sub_categories
	return frappe.db.sql("""
		SELECT DISTINCT b.name, b.brand_name
		FROM `tabBrands` b
		INNER JOIN `tabSub Categories` sc ON sc.parent = b.name
		WHERE sc.item_group = %(item_group)s
		AND b.name LIKE %(txt)s
		ORDER BY b.brand_name
		LIMIT %(start)s, %(page_len)s
	""", {
		"item_group": item_group,
		"txt": "%" + txt + "%",
		"start": start,
		"page_len": page_len
	})


@frappe.whitelist()
def get_catalogues_by_brand(brand):
	"""
	Get catalogues from the selected brand's catalogue child table.
	Returns list of catalogue names for the select field options.
	"""
	if not brand:
		return []
	
	catalogues = frappe.db.sql("""
		SELECT catalogue
		FROM `tabCatalogues`
		WHERE parent = %(brand)s
		ORDER BY catalogue
	""", {
		"brand": brand
	}, as_dict=True)
	
	return [cat.catalogue for cat in catalogues]


@frappe.whitelist()
def check_item_group_in_brands(item_group):
	"""
	Check if the specified item group exists in any brand's sub_categories.
	Returns True if found, False otherwise.
	"""
	if not item_group:
		return False
	
	result = frappe.db.sql("""
		SELECT COUNT(*) as count
		FROM `tabSub Categories` sc
		WHERE sc.item_group = %(item_group)s
	""", {
		"item_group": item_group
	}, as_dict=True)
	
	return result[0].count > 0 if result else False
