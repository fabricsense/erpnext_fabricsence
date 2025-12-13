# Services and Category DocTypes

## Overview

This guide explains how to create two new DocTypes in the Fabric Sense app using Frappe/ERPNext best practices:

- Category (master)
- Services (links to Category) with a child table Contractors List

It includes Desk UI steps, bench CLI equivalents, export instructions, and unit test skeletons. Follow the same pattern used in other detailed sections under `docs/datailed_sections/`.

---

## Prerequisites & Permissions

- **Role**: System Manager (to create DocTypes and customize)
- **App/Module**: Fabric Sense → Module name per `fabric_sense/fabric_sense/modules.txt` (e.g., "Fabric Sense")
- **Environment**: Development site; run `bench --site <yoursite>` for CLI operations

---

## Doctype Definitions

### 1) Category
- **Doctype Name**: Category
- **Module**: Fabric Sense (or your chosen module within the app)
- **Is Submittable**: No
- **Title Field**: Category Name

Fields:
- **Category Name** (Data) — Mandatory
- **Description** (Small Text) — Optional

### 2) Child Table: Contractors List
- **Doctype Name**: Contractors List
- **Module**: Fabric Sense
- **Is Child Table**: Yes

Fields:
- **Contractor** (Link → Employee)
- **Rate** (Currency)

### 3) Services
- **Doctype Name**: Services
- **Module**: Fabric Sense
- **Is Submittable**: No
- **Title Field**: Service Name

Fields:
- **Service Name** (Data)
- **Category** (Link → Category)
- **Contractors** (Table → Contractors List)

Note: In `Services`, the table field label is `Contractors` and the fieldname is `contractors` (pointing to child table doctype `Contractors List`).

---

## Create via Desk (No Coding)

1. **Create Category**
   - Desk → Settings → DocType → New
   - Name: `Category`
   - Module: `Fabric Sense`
   - Uncheck "Is Submittable"
   - Fields:
     - Row 1: Label `Category Name`, Type `Data`, Mandatory
     - Row 2: Label `Description`, Type `Small Text`
   - Title Field: set to `Category Name`
   - Save

2. **Create Child Table: Contractors List**
   - Desk → Settings → DocType → New
   - Name: `Contractors List`
   - Module: `Fabric Sense`
   - Check "Is Child Table"
   - Fields:
     - Row 1: Label `Contractor`, Type `Link`, Options `Employee`
     - Row 2: Label `Rate`, Type `Currency`
   - Save

3. **Create Services**
   - Desk → Settings → DocType → New
   - Name: `Services`
   - Module: `Fabric Sense`
   - Uncheck "Is Submittable"
   - Fields:
     - Row 1: Label `Service Name`, Type `Data`
     - Row 2: Label `Category`, Type `Link`, Options `Category`
     - Row 3: Label `Contractors`, Type `Table`, Options `Contractors List`
   - Title Field: set to `Service Name`
   - Save

4. **Export Customizations (Recommended)**
   - From any of the DocTypes, click `Menu → Export Customizations`
   - Module: `fabric_sense`
   - Submit
   - JSON files will be created under `fabric_sense/fabric_sense/doctype/...` or `fabric_sense/fabric_sense/custom/` per your setup

5. **Commit & Migrate to other sites**
   - Add and commit exported files to your repo
   - On target site: install the app (if not installed) and run `bench migrate`

---

## Create via Bench CLI (Alternative)

Replace `<site-name>` with your site.

```bash
# Ensure correct site context
bench --site <site-name> set-config developer_mode 1

# Create DocTypes
bench --site <site-name> new-doctype "Category" \
  --module "Fabric Sense" --custom --autoname "field:category_name"

bench --site <site-name> new-doctype "Contractors List" \
  --module "Fabric Sense" --is-child-table 1 --custom

bench --site <site-name> new-doctype "Services" \
  --module "Fabric Sense" --custom --autoname "field:service_name"
```

Then open each doctype in Desk to add fields and set the Title Field as specified above. Alternatively, edit the JSONs and run `bench migrate`.

Build assets if you added any client scripts for these doctypes:

```bash
bench build --app fabric_sense
bench clear-cache
bench restart
```

---

## Validation & Behavior (Optional Enhancements)

- Add unique constraint on `Category Name` if needed
- Add validations in `Services` to ensure `Category` is set
- Consider making `Rate` in child rows mandatory if your process requires it

---

## Unit Tests

Place tests under the doctype package directories. Example structure:

- `fabric_sense/fabric_sense/doctype/category/test_category.py`
- `fabric_sense/fabric_sense/doctype/contractors_list/test_contractors_list.py`
- `fabric_sense/fabric_sense/doctype/services/test_services.py`

Example test skeletons:

```python
# file: fabric_sense/fabric_sense/doctype/category/test_category.py
import frappe


def test_create_category():
    cat = frappe.get_doc({
        "doctype": "Category",
        "category_name": "Curtains",
        "description": "Curtain related services"
    }).insert()

    assert cat.name
    assert cat.category_name == "Curtains"
```

```python
# file: fabric_sense/fabric_sense/doctype/contractors_list/test_contractors_list.py
import frappe


def test_child_row_schema_exists():
    meta = frappe.get_meta("Contractors List")
    fields = {df.fieldname: df for df in meta.fields}
    assert "contractor" in fields
    assert fields["contractor"].options == "Employee"
    assert "rate" in fields
```

```python
# file: fabric_sense/fabric_sense/doctype/services/test_services.py
import frappe


def test_create_service_with_category_and_child_table():
    cat = frappe.get_doc({
        "doctype": "Category",
        "category_name": "Blinds"
    }).insert(ignore_if_duplicate=True)

    svc = frappe.get_doc({
        "doctype": "Services",
        "service_name": "Roman Blind Installation",
        "category": cat.name,
        "contractors": [
            {"contractor": frappe.db.get_value("Employee", {"status": "Active"}, "name"), "rate": 150.0}
        ]
    }).insert()

    assert svc.name
    assert svc.category == cat.name
    assert len(svc.contractors) >= 1
```

Run tests:

```bash
bench --site <site-name> run-tests --doctype Category Services "Contractors List"
```

---

## User Flow (Process)

1. Create one or more `Category` records (e.g., Curtains, Blinds, Tracks)
2. Create `Services` and link to a `Category`
3. Add rows in `Contractors List` with `Contractor` (Employee) and `Rate`
4. Use `Services` in quoting or internal planning as needed

---

## Troubleshooting

- **DocType not visible**: Check role permissions for the DocType
- **Child table not appearing**: Ensure `Contractors List` is set as Options for the Table field in `Services`
- **Title field not showing**: In DocType, set `Title Field` appropriately (Category Name / Service Name) and reload
- **Tests failing**: Ensure an `Employee` record exists for link field tests or mock one in the test

---

## Notes

- Keep naming consistent with other detailed sections.
- Consider later adding client-side scripts or server hooks if business rules grow.
