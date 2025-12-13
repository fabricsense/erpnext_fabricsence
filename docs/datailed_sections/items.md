# Item Pricing and SKU Customization

## Overview

This guide explains how to add SKU fields to selling documents and how to implement the **Base Rate + Markup Percentage** pricing model so Item Prices are calculated automatically. Follow the steps in order: add custom fields, connect pricing logic, and verify the user flow.

---

## Add SKU Field to Sales Documents

### Objective

Ensure Sales Order, Sales Invoice, and Delivery Note capture the SKU for each line item.

### Steps

1. Open **Customize Form** for each doctype: **Sales Order Item**, **Sales Invoice Item**, **Delivery Note Item**.
2. Add a custom field:
   - **Field Name**: `sku`
   - **Label**: SKU
   - **Field Type**: Data
   - **Insert After**: `item_code` (or near other item identifiers)
   - **In List View**: Enable if you want SKU visible in the item table.
3. Save and **Export Customizations** to the `fabric_sense` module so the JSON files are stored under `fabric_sense/fabric_sense/custom/`.

---

## Base Rate Field in Item

### Objective

Store the primary cost for each item to drive markup-based pricing.

### Steps

1. Go to **Customize Form** → **Item**.
2. Add a custom field:
   - **Field Name**: `base_rate`
   - **Label**: Base Rate
   - **Field Type**: Currency
   - **Description**: The original/basic cost of the item.
3. Save and export the customization to capture it in version control.

---

## Markup Percentage in Item Price

### Objective

Define the markup that will be applied to the Item’s Base Rate to derive the selling price for a specific Price List / Customer Group.

### Steps

1. Open **Customize Form** → **Item Price**.
2. Add a custom field:
   - **Field Name**: `markup_percentage`
   - **Label**: Markup Percentage
   - **Field Type**: Float
   - **Description**: Percentage used to calculate selling price from Base Rate.
3. Save and export the customization.

---

## Auto-Calculate Selling Price on Item Price

### Objective

Automatically set the Item Price `rate` using the Item’s `base_rate` and the Item Price’s `markup_percentage`.

### Steps

1. Add a client script for **Item Price** to compute rate:
   - Fetch `base_rate` from the linked Item.
   - Calculate `rate = base_rate + (base_rate * (markup_percentage / 100))`.
   - Set `price_list_rate` (or `rate`) accordingly.
2. Place the JS at `fabric_sense/public/js/item_price.js` and link it in `hooks.py` via `doctype_js = {"Item Price": "public/js/item_price.js"}` if not already present.
3. Build assets and clear cache:
   ```bash
   bench build --app fabric_sense
   bench clear-cache
   ```

---

## Keep Item Price in Sync When Inputs Change

### Objective

Ensure Item Prices update whenever `base_rate` or `markup_percentage` changes.

### Steps

1. In the Item Price client script, recompute on:
   - `item_code` change (pull latest `base_rate`)
   - `markup_percentage` change
   - Form refresh (to reflect any upstream changes)
2. If Base Rate is edited on Item:
   - Update the Item.
   - Reopen the related Item Price and let the script recalc, or add a server-side job to recalc Item Prices tied to that Item.
3. Confirm the script uses the correct fields (`base_rate` on Item and `markup_percentage` on Item Price) and writes to `price_list_rate`.

---

## User Flow Summary

- Maintain **Base Rate** on Item.
- Set **Markup Percentage** on Item Price for each Price List / Customer Group.
- The Item Price form auto-calculates **Selling Price** (Price List Rate) from Base Rate + Markup.
- Sales documents capture SKU alongside Item Code for downstream visibility.

---

## Unit Test Cases

- **Base rate with percentage markup**: Item base rate 100, Item Price markup `10%` → price list rate updates to 110.
- **Base rate with multiplier**: Item base rate 100, markup `1.5` (no `%`) → price list rate updates to 150.
- **Missing markup defaults to base**: Item base rate 100, markup empty → price list rate stays 100.
- **Refresh recomputes**: Open Item Price with existing item_code and empty price_list_rate → script fetches base and fills price_list_rate.
- **Invalid percentage**: Item base rate 100, markup `abc%` → shows “Invalid percentage value” and does not change price_list_rate.
- **Negative percentage lower bound**: Item base rate 100, markup `-150%` → shows “Percentage cannot be less than -100%” and does not change price_list_rate.
- **Negative multiplier**: Item base rate 100, markup `-1` → shows “Multiplier cannot be negative” and does not change price_list_rate.
- **Negative base rate**: Item base rate `-1` → shows “Base rate cannot be negative” and does not change price_list_rate.
- **Item change re-fetch**: Change item_code on Item Price → script fetches that item’s base and recalculates price_list_rate.

---

## Verification

1. Create or edit an Item and set **Base Rate**.
2. Create an Item Price for that Item, select a Price List, set **Markup Percentage**, and verify **Price List Rate** auto-fills.
3. Create Sales Order / Sales Invoice / Delivery Note lines:
   - Add Item Code; ensure SKU field is available and can be filled.
   - Confirm pricing matches the computed Item Price.
4. Check browser console for JS errors; rebuild/clear cache if scripts change.

