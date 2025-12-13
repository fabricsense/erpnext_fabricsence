# Sales Order from Measurement Sheet - Technical Implementation

This document summarizes the technical implementation details for creating Sales Orders from approved Measurement Sheets, focusing on server/client logic, data mapping, and code structure. Use this when onboarding engineers or debugging.

---

## Components
- Server method: `fabric_sense/fabric_sense/doctype/measurement_sheet/measurement_sheet.py`
- Client script: `fabric_sense/fabric_sense/doctype/measurement_sheet/measurement_sheet.js`
- Helper functions: `fabric_sense/public/js/helpers/measurement_sheet_helpers.js`
- Custom field: `fabric_sense/fabric_sense/custom/sales_order.json`

---

## Server-Side Implementation

### Main Method: `get_sales_order_data_from_measurement_sheet()`

**Location:** `fabric_sense/fabric_sense/doctype/measurement_sheet/measurement_sheet.py`

**Signature:**
```python
@frappe.whitelist()
def get_sales_order_data_from_measurement_sheet(measurement_sheet_name: str) -> Dict[str, Any]
```

**Flow:**
1. Permission check using `frappe.has_permission()`
2. Load Measurement Sheet document
3. Validate status is "Approved"
4. Validate customer exists
5. Validate measurement details exist
6. Batch query selection item rates (avoids N+1)
7. Extract items from measurement details
8. Validate at least one item found
9. Return data dictionary

**Returns:**
```python
{
    "customer": str,
    "transaction_date": str,  # frappe.utils.today()
    "measurement_sheet": str,
    "project": str | None,
    "items": List[Dict[str, Any]]  # Each item: {"item_code": str, "qty": float, "rate": float, "idx": int}
}
```

**Error Handling:**
- All validation errors logged using `frappe.log_error()`
- Permission errors throw `frappe.PermissionError`
- Validation errors throw `frappe.ValidationError` with context

### Helper Functions

#### `_add_item_if_valid()`
- Adds regular items (fabric, lining, lead_rope, track_rod) to items list
- Validates: item_code exists, qty > 0
- Returns next item index

#### `_add_service_charge_item_if_valid()`
- Adds service charge items (stitching, fitting) to items list
- Validates: item_code exists, charge > 0
- Sets qty = 1 (SERVICE_CHARGE_QTY constant)
- Returns next item index

#### `_get_selection_item_rates()`
- Batch queries Item Prices for selection items (Blinds)
- Removes duplicates before querying
- Falls back to Item.standard_rate if no Item Price found
- Ensures all items have a rate (defaults to 0.0)
- Returns Dict[item_code, rate]

#### `_extract_items_from_measurement_details()`
- Iterates through measurement_details
- Calls helper functions to add items
- Handles selection items separately (uses pre-fetched rates)
- Returns complete items list

### Constants
- `STATUS_APPROVED = "Approved"`
- `SERVICE_CHARGE_QTY = 1`
- `SELECTION_ITEM_QTY = 1`

---

## Client-Side Implementation

### Helper Function: `create_sales_order_from_measurement_sheet()`

**Location:** `fabric_sense/public/js/helpers/measurement_sheet_helpers.js`

**Button Visibility Conditions:**
- Form exists and is not new (`!frm.is_new()`)
- Document has a name (is saved)
- Document has no unsaved changes (`!frm.is_dirty()`)
- Status is "Approved" (`frm.doc.status === STATUS_APPROVED`)

**Flow:**
1. Add custom button "Create Sales Order" under "Create" menu
2. On click, call server method `get_sales_order_data_from_measurement_sheet()`
3. Validate response structure
4. Validate customer exists
5. Validate items array exists and has items
6. Create new Sales Order using `frappe.model.get_new_doc()`
7. Populate top-level fields (customer, transaction_date, measurement_sheet, project)
8. Add items using `frappe.model.add_child()` with validation
9. Navigate to pre-filled form using `frappe.set_route()`

**Validation:**
- Response structure validation
- Customer field validation
- Items array validation (exists, is array, has length > 0)
- Individual item validation (item_code exists, qty > 0)
- Fallback for transaction_date using `frappe.datetime.get_today()`

**Error Handling:**
- Invalid response: Shows error message
- Missing customer: Shows error message
- No items: Shows warning message
- Server errors: Shows error message with server response

### Integration Point

**File:** `fabric_sense/fabric_sense/doctype/measurement_sheet/measurement_sheet.js`

**In `refresh()` handler:**
```javascript
msHelper.create_sales_order_from_measurement_sheet(frm);
```

---

## Data Mapping

### Measurement Sheet → Sales Order

| Measurement Sheet Field | Sales Order Field | Notes |
|------------------------|-------------------|-------|
| `customer` | `customer` | Direct mapping |
| `project` | `project` | Optional, only if exists |
| `name` | `measurement_sheet` | Link field (read-only) |
| Current date | `transaction_date` | `frappe.utils.today()` |

### Measurement Detail → Sales Order Item

| Measurement Detail Field | Sales Order Item Field | Quantity | Rate |
|-------------------------|------------------------|----------|------|
| `fabric_selected` | `item_code` | `fabric_qty` | `fabric_rate` |
| `lining` | `item_code` | `lining_qty` | `lining_rate` |
| `lead_rope` | `item_code` | `lead_rope_qty` | `lead_rope_rate` |
| `track_rod` | `item_code` | `track_rod_qty` | `track_rod_rate` |
| `selection` | `item_code` | `1` | From Item Price or standard_rate |
| `stitching_pattern` | `item_code` | `1` | `stitching_charge` |
| `fitting_type` | `item_code` | `1` | `fitting_charge` |

**Rules:**
- Only items with valid item_code and qty > 0 are added
- Each item becomes a separate row
- Service charges always have qty = 1
- Selection items use batch-queried rates

---

## Performance Optimizations

### Batch Queries
- Selection item rates queried in batch (prevents N+1 query problem)
- Duplicate items removed before querying
- Single query for all Item Prices, single query for all Item standard_rates

### Code Organization
- Helper functions reduce code duplication
- Constants prevent magic numbers
- Type hints improve IDE support and code quality

---

## Security

### Permission Checks
- Server method checks read permission on Measurement Sheet
- Unauthorized access attempts are logged

### Validation
- Status validation (must be "Approved")
- Customer validation (must exist)
- Measurement details validation (must exist)
- Items validation (at least one valid item)

### Field Security
- `measurement_sheet` field in Sales Order is read-only (auto-populated)

---

## Error Handling

### Server-Side
- All errors logged with context (measurement sheet name, status, user)
- Descriptive error messages include measurement sheet name
- Permission errors use `frappe.PermissionError`
- Validation errors use `frappe.ValidationError`

### Client-Side
- Response structure validation
- Field validation before processing
- User-friendly error messages
- Graceful handling of missing data

---

## Integration Points

### Measurement Sheet
- Reads from Measurement Sheet doctype
- Validates status field
- Extracts data from measurement_details child table

### Sales Order
- Creates new Sales Order document
- Populates custom field `measurement_sheet`
- Links back to source Measurement Sheet

### Item Master
- Queries Item Price for selection items
- Falls back to Item.standard_rate
- Validates item codes exist

---

## Dev Notes

### Document Creation
- Uses `frappe.model.get_new_doc()` for model-layer creation
- Ensures document is properly initialized before form loads
- Child rows added using `frappe.model.add_child()`

### Button Visibility
- Button only shows when document is saved and approved
- Checks `frm.is_dirty()` to prevent showing on unsaved changes
- Status check uses constant `STATUS_APPROVED`

### Rate Fetching
- Selection items use batch query to avoid N+1 problem
- Rates default to 0.0 if not found
- Explicit float conversion for type safety

### Code Quality
- All functions have type hints
- Constants extracted for maintainability
- Helper functions keep main function concise
- Comprehensive error logging

---

## Future Enhancements

- Support for additional item types
- Bulk Sales Order creation from multiple Measurement Sheets
- Automatic rate updates based on Price Lists
- Integration with Material Request creation

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Author**: Fabric Sense Development Team

