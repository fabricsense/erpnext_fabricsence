# Frappe Code Review Guidelines

## Table of Contents
1. [Overview](#overview)
2. [Review Process](#review-process)
3. [Structure & Organization](#structure--organization)
4. [Python Quality Standards](#python-quality-standards)
5. [JavaScript Quality Standards](#javascript-quality-standards)
6. [Security & Validation](#security--validation)
7. [Issue Prioritization](#issue-prioritization)
8. [Review Checklist](#review-checklist)
9. [Common Patterns & Anti-patterns](#common-patterns--anti-patterns)

---

## Overview

This document defines the code review standards and guidelines for Frappe-based applications. All code should be reviewed against these criteria before merging to ensure maintainability, security, and adherence to Frappe best practices.

### Review Objectives
- **Maintainability**: Code should be easy to understand, modify, and extend
- **Security**: Proper permission checks, validation, and transaction handling
- **Performance**: Efficient database queries and minimal DOM operations
- **Consistency**: Follow Frappe conventions and project patterns
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion

---

## Review Process

### Review Steps
1. **Structure Check**: Identify files >250 lines, check separation of concerns
2. **Language-Specific Review**: Apply Python/JavaScript quality standards
3. **Security Audit**: Verify permissions, validation, and transaction handling
4. **Performance Analysis**: Check for N+1 queries, unnecessary DOM ops
5. **Documentation**: Ensure docstrings, comments, and type hints where needed

### Output Format
For each issue found, provide:
- **File Path**: Exact location of the issue
- **Priority**: Critical > High > Medium > Low
- **Problem Description**: Clear explanation of the issue
- **Current Code Snippet**: Relevant code showing the problem
- **Refactored Version**: Suggested improvement
- **Explanation**: Why the refactor improves the code

---

## Structure & Organization

### File Size Limits
- **JavaScript Files**: Should not exceed 250 lines
  - **Action**: Extract helper functions to `public/js/helpers/` directory
  - **Rationale**: Large files are harder to maintain and test
  - **Exception**: Auto-generated files or configuration files

- **Python Files**: Should not exceed 250 lines
  - **Action**: Extract utility functions to `utils/` directory
  - **Rationale**: Promotes reusability and testability

### Code Organization

#### Separation of Concerns
- **Form Scripts** (`doctype/*/doctype.js`): Should only contain event handlers
- **Helper Functions**: Business logic, calculations, and utilities should be in helper modules
- **Server Methods**: Python business logic should be in separate utility modules when complex

#### Code Duplication
- **Flag**: Any code block repeated 2+ times
- **Action**: Extract to shared function/utility
- **Rationale**: DRY (Don't Repeat Yourself) principle reduces maintenance burden

#### SOLID Principles Compliance

**Single Responsibility Principle (SRP)**
- Each function/class should have one reason to change
- Example: Calculation functions should not also handle UI updates

**Open/Closed Principle (OCP)**
- Code should be open for extension, closed for modification
- Use configuration objects, callbacks, or inheritance patterns

**Liskov Substitution Principle (LSP)**
- Subtypes must be substitutable for their base types
- Ensure custom DocTypes properly extend Frappe Document class

**Interface Segregation Principle (ISP)**
- Clients should not depend on interfaces they don't use
- Keep helper functions focused and minimal

**Dependency Inversion Principle (DIP)**
- Depend on abstractions, not concretions
- Use dependency injection for testability

---

## Python Quality Standards

### Frappe Best Practices

#### Database Queries
- **Use `frappe.db.get_value()`** for single value lookups
- **Use `frappe.db.get_list()`** for multiple records
- **Use `frappe.db.get_all()`** for full document access
- **Avoid N+1 Queries**: Batch queries when possible
  ```python
  # ❌ Bad: N+1 query problem
  for row in self.measurement_details:
      item = frappe.db.get_value("Item", row.item_code, "item_name")
  
  # ✅ Good: Batch query
  item_codes = [row.item_code for row in self.measurement_details]
  items = frappe.db.get_value("Item", {"name": ["in", item_codes]}, ["name", "item_name"], as_dict=True)
  item_map = {item.name: item.item_name for item in items}
  ```

#### Error Handling
- **Always use `frappe.throw()`** for validation errors with user-friendly messages
- **Use `frappe.log_error()`** for unexpected errors
- **Handle exceptions** in critical paths
  ```python
  # ✅ Good
  try:
      result = complex_calculation()
  except Exception as e:
      frappe.log_error(f"Calculation failed: {str(e)}", "Measurement Sheet Error")
      frappe.throw("An error occurred during calculation. Please contact support.")
  ```

#### Whitelisted Methods
- **All server methods must be whitelisted** using `@frappe.whitelist()`
- **Add permission checks** in whitelisted methods
  ```python
  @frappe.whitelist()
  def get_item_rate(item_code):
      # Check permissions
      if not frappe.has_permission("Item", "read"):
          frappe.throw("Insufficient permissions", frappe.PermissionError)
      
      return frappe.db.get_value("Item", item_code, "standard_rate")
  ```

### Code Quality Metrics

#### Function Length
- **Maximum**: 50 lines per function
- **Action**: Break into smaller, focused functions
- **Rationale**: Easier to test, understand, and maintain

#### Nested Complexity
- **Maximum**: 3 levels of nesting
- **Action**: Extract nested blocks to separate functions
- **Rationale**: Reduces cognitive load and improves readability

#### Hardcoded Values
- **Flag**: Magic numbers, strings, or configuration values
- **Action**: Extract to constants or configuration
  ```python
  # ❌ Bad
  if status == "Approved":
      send_notification()
  
  # ✅ Good
  STATUS_APPROVED = "Approved"
  if status == STATUS_APPROVED:
      send_notification()
  ```

### Code Style

#### PEP 8 Compliance
- Follow Python PEP 8 style guide
- Use 4 spaces for indentation (tabs are not allowed)
- Maximum line length: 100 characters (Frappe standard)
- Use descriptive variable and function names

#### Type Hints
- **Recommended**: Add type hints for function parameters and return values
- **Required**: For complex functions or public APIs
  ```python
  from typing import List, Dict, Optional
  
  def calculate_totals(details: List[Dict]) -> float:
      """Calculate total amount from measurement details."""
      return sum(row.get("amount", 0) for row in details)
  ```

#### Docstrings
- **Required**: For all public functions and classes
- **Format**: Google or NumPy style
  ```python
  def validate_measurement_details(self):
      """
      Validate that measurement details table has at least one row.
      
      Raises:
          frappe.ValidationError: If no measurement details are provided.
      """
      if not self.measurement_details or len(self.measurement_details) == 0:
          frappe.throw("At least one Measurement Detail is required")
  ```

### Database Query Optimization

#### N+1 Query Problems
- **Flag**: Loops containing database queries
- **Action**: Batch queries or use joins
- **Example**: See Database Queries section above

#### Index Usage
- Ensure queries use indexed fields when possible
- Use `explain()` to analyze query performance for complex queries

#### Transaction Handling
- Use `frappe.db.commit()` sparingly (Frappe handles transactions automatically)
- Only commit when necessary (e.g., after critical operations)
- Use `frappe.db.rollback()` for error recovery

---

## JavaScript Quality Standards

### Frappe Patterns

#### Form Event Handlers
- **Use `frappe.ui.form.on()`** for form events
- **Keep handlers thin**: Delegate to helper functions
  ```javascript
  // ❌ Bad: Business logic in event handler
  frappe.ui.form.on("Measurement Sheet", {
      refresh(frm) {
          let total = 0;
          frm.doc.measurement_details.forEach(row => {
              total += parseFloat(row.amount) || 0;
          });
          frm.set_value("total_amount", total);
      }
  });
  
  // ✅ Good: Delegate to helper
  frappe.ui.form.on("Measurement Sheet", {
      refresh(frm) {
          msHelper.calculate_totals(frm);
      }
  });
  ```

#### Server Calls
- **Use `frappe.call()`** for server-side method calls
- **Handle errors** in callbacks
- **Use async/await** when possible (modern Frappe versions)
  ```javascript
  // ✅ Good: Modern async/await pattern
  async function fetch_item_rate(item_code) {
      try {
          const result = await frappe.db.get_value("Item", item_code, "standard_rate");
          return result?.message?.standard_rate || 0;
      } catch (error) {
          frappe.show_alert({ message: "Error fetching rate", indicator: "red" }, 5);
          return 0;
      }
  }
  
  // ✅ Good: Traditional callback pattern
  frappe.call({
      method: "fabric_sense.api.get_item_rate",
      args: { item_code: item_code },
      callback: function(r) {
          if (r.message) {
              // Handle success
          }
      },
      error: function(r) {
          frappe.show_alert({ message: "Error occurred", indicator: "red" }, 5);
      }
  });
  ```

### Code Quality Metrics

#### Function Length
- **Maximum**: 40 lines per function
- **Action**: Extract logic to helper functions
- **Rationale**: JavaScript functions should be focused and testable

#### Code Duplication
- **Flag**: Repeated code blocks
- **Action**: Extract to shared helper functions
- **Location**: Place in `public/js/helpers/` directory

#### Error Handling
- **Required**: For all async operations
- **Use try/catch** with async/await
- **Show user feedback** for errors
  ```javascript
  // ✅ Good
  async function calculate_amounts(frm, cdt, cdn) {
      try {
          const row = locals[cdt][cdn];
          const amount = await compute_amount(row);
          await frappe.model.set_value(cdt, cdn, "amount", amount);
      } catch (error) {
          frappe.log_error(`Error calculating amounts: ${error.message}`, "Calculation Error");
          frappe.show_alert({ message: "Calculation failed", indicator: "red" }, 5);
      }
  }
  ```

### Performance Considerations

#### DOM Operations
- **Minimize**: Reduce unnecessary `refresh_field()` calls
- **Batch**: Group multiple field updates
- **Debounce**: Use debouncing for rapid-fire events
  ```javascript
  // ❌ Bad: Multiple refresh calls
  function update_row(frm, cdt, cdn) {
      frappe.model.set_value(cdt, cdn, "field1", value1);
      frm.refresh_field("measurement_details");
      frappe.model.set_value(cdt, cdn, "field2", value2);
      frm.refresh_field("measurement_details");
  }
  
  // ✅ Good: Batch updates
  async function update_row(frm, cdt, cdn) {
      await frappe.model.set_value(cdt, cdn, {
          field1: value1,
          field2: value2
      });
      frm.refresh_field("measurement_details");
  }
  ```

#### Debouncing
- **Use for**: Rapid-fire events (typing, calculations)
- **Implementation**: Use `setTimeout` with clear
  ```javascript
  let calculationTimer = null;
  
  function debounced_calculate(frm, cdt, cdn) {
      if (calculationTimer) {
          clearTimeout(calculationTimer);
      }
      calculationTimer = setTimeout(() => {
          perform_calculation(frm, cdt, cdn);
      }, 50);
  }
  ```

#### Caching
- **Cache**: Expensive operations (database queries, calculations)
- **Clear**: Cache on relevant data changes
  ```javascript
  const itemRateCache = {};
  
  function fetch_item_rate(item_code) {
      if (itemRateCache[item_code] !== undefined) {
          return Promise.resolve(itemRateCache[item_code]);
      }
      return frappe.db.get_value("Item", item_code, "standard_rate").then(r => {
          const rate = r?.message?.standard_rate || 0;
          itemRateCache[item_code] = rate;
          return rate;
      });
  }
  ```

### Helper Function Organization

#### File Structure
- **Location**: `public/js/helpers/`
- **Naming**: `{doctype}_helpers.js` or `{feature}_helpers.js`
- **Namespace**: Use `frappe.provide()` for namespacing
  ```javascript
  frappe.provide("fabric_sense.measurement_sheet");
  
  fabric_sense.measurement_sheet.calculate_totals = function(frm) {
      // Implementation
  };
  ```

#### Helper Requirements
- **Pure Functions**: When possible, make functions pure (no side effects)
- **Single Responsibility**: Each function should do one thing
- **Reusability**: Design for reuse across multiple contexts

---

## Security & Validation

### Permission Checks

#### Whitelisted Methods
- **Required**: Permission checks in all whitelisted methods
- **Check**: User has required permissions before operations
  ```python
  @frappe.whitelist()
  def update_measurement_sheet(name, data):
      # Check permissions
      if not frappe.has_permission("Measurement Sheet", "write"):
          frappe.throw("Insufficient permissions", frappe.PermissionError)
      
      doc = frappe.get_doc("Measurement Sheet", name)
      doc.update(data)
      doc.save()
      return doc.as_dict()
  ```

#### Field-Level Permissions
- **Respect**: Frappe's built-in permission system
- **Don't bypass**: Client-side validation is not security

### Client/Server Validation Consistency

#### Validation Rules
- **Client-side**: For UX (immediate feedback)
- **Server-side**: For security (always validate on server)
- **Consistency**: Same rules on both sides
  ```python
  # Server-side (Python)
  def validate(self):
      if not self.measurement_details or len(self.measurement_details) == 0:
          frappe.throw("At least one Measurement Detail is required")
  ```
  ```javascript
  // Client-side (JavaScript) - Same validation
  frappe.ui.form.on("Measurement Sheet", {
      validate(frm) {
          if (!frm.doc.measurement_details || frm.doc.measurement_details.length === 0) {
              frappe.msgprint("At least one Measurement Detail is required");
              frappe.validated = false;
          }
      }
  });
  ```

### Transaction Handling

#### Database Transactions
- **Automatic**: Frappe handles transactions automatically
- **Manual**: Only when necessary (e.g., complex multi-doc operations)
  ```python
  def create_sales_order(self):
      try:
          frappe.db.begin()
          # Create multiple documents
          sales_order = frappe.get_doc({...})
          sales_order.insert()
          # ... more operations
          frappe.db.commit()
      except Exception as e:
          frappe.db.rollback()
          frappe.throw(f"Error creating sales order: {str(e)}")
  ```

#### Error Recovery
- **Rollback**: On critical errors
- **Log**: All errors for debugging
- **User Feedback**: Clear error messages

---

## Issue Prioritization

### Priority Levels

#### Critical
- **Security vulnerabilities**: Permission bypasses, SQL injection risks
- **Data integrity issues**: Transaction problems, data loss risks
- **Breaking changes**: Code that will cause runtime errors

#### High
- **Performance issues**: N+1 queries, memory leaks, excessive DOM operations
- **Code organization**: Files >250 lines, major duplication
- **Maintainability**: Complex functions, poor separation of concerns

#### Medium
- **Code quality**: Functions >50 lines (Python) or >40 lines (JavaScript)
- **Best practices**: Missing type hints, docstrings, error handling
- **Refactoring opportunities**: Code that works but could be improved

#### Low
- **Style issues**: Minor formatting, naming conventions
- **Documentation**: Missing comments, unclear variable names
- **Optimization**: Minor performance improvements

### Priority Assignment Guidelines

1. **Security & Data Integrity** → Always Critical
2. **User-Facing Bugs** → High (if blocking) or Medium (if minor)
3. **Performance** → High (if significant impact) or Medium (if minor)
4. **Code Quality** → Medium (if affects maintainability) or Low (if cosmetic)
5. **Documentation** → Low (unless critical for understanding)

---

## Review Checklist

### Pre-Review
- [ ] Code follows project structure conventions
- [ ] No hardcoded credentials or sensitive data
- [ ] All files are properly formatted

### Structure & Organization
- [ ] No files exceed 250 lines
- [ ] Helper functions extracted to appropriate directories
- [ ] No significant code duplication
- [ ] SOLID principles followed

### Python Code
- [ ] Functions ≤50 lines
- [ ] No N+1 query problems
- [ ] Proper error handling with `frappe.throw()` and `frappe.log_error()`
- [ ] All whitelisted methods have permission checks
- [ ] Type hints for complex functions
- [ ] Docstrings for public functions/classes
- [ ] PEP 8 compliance
- [ ] No hardcoded values (use constants)

### JavaScript Code
- [ ] Functions ≤40 lines
- [ ] Event handlers delegate to helper functions
- [ ] Proper error handling in async operations
- [ ] Debouncing for rapid-fire events
- [ ] Caching for expensive operations
- [ ] Minimal DOM operations
- [ ] Helper functions in `public/js/helpers/`
- [ ] No global variable pollution (use namespaces)

### Security & Validation
- [ ] Permission checks in whitelisted methods
- [ ] Server-side validation matches client-side
- [ ] Proper transaction handling
- [ ] No SQL injection risks
- [ ] Input sanitization where needed

### Performance
- [ ] No N+1 database queries
- [ ] Efficient use of `frappe.db` methods
- [ ] Minimal unnecessary DOM refreshes
- [ ] Debouncing/caching where appropriate

### Documentation
- [ ] Complex logic has comments
- [ ] Public APIs have docstrings
- [ ] README updated if needed

---

## Common Patterns & Anti-patterns

### ✅ Good Patterns

#### Helper Function Extraction
```javascript
// Helper module: public/js/helpers/measurement_sheet_helpers.js
frappe.provide("fabric_sense.measurement_sheet");
fabric_sense.measurement_sheet.calculate_totals = function(frm) {
    // Implementation
};

// Form script: measurement_sheet.js
frappe.require("/assets/fabric_sense/js/helpers/measurement_sheet_helpers.js");
frappe.ui.form.on("Measurement Sheet", {
    refresh(frm) {
        fabric_sense.measurement_sheet.calculate_totals(frm);
    }
});
```

#### Batch Database Queries
```python
# ✅ Good: Batch query
item_codes = [row.item_code for row in self.measurement_details]
items = frappe.db.get_list("Item", filters={"name": ["in", item_codes]}, fields=["name", "standard_rate"])
item_map = {item.name: item.standard_rate for item in items}
```

#### Async/Await Pattern
```javascript
// ✅ Good: Modern async pattern
async function fetch_and_set_rate(frm, cdt, cdn, item_code) {
    try {
        const rate = await fetch_item_rate(item_code);
        await frappe.model.set_value(cdt, cdn, "rate", rate);
        calculate_amounts(frm, cdt, cdn);
    } catch (error) {
        frappe.log_error(error.message, "Rate Fetch Error");
    }
}
```

### ❌ Anti-patterns

#### Business Logic in Event Handlers
```javascript
// ❌ Bad: Business logic in event handler
frappe.ui.form.on("Measurement Sheet", {
    refresh(frm) {
        let total = 0;
        frm.doc.measurement_details.forEach(row => {
            // Complex calculation logic here
            total += parseFloat(row.amount) || 0;
        });
        frm.set_value("total_amount", total);
    }
});
```

#### N+1 Query Problem
```python
# ❌ Bad: N+1 queries
for row in self.measurement_details:
    item = frappe.db.get_value("Item", row.item_code, "item_name")
    # Process item
```

#### Deep Promise Nesting
```javascript
// ❌ Bad: Deep nesting
frappe.model.set_value(cdt, cdn, "field1", value1).then(() => {
    frappe.model.set_value(cdt, cdn, "field2", value2).then(() => {
        frappe.model.set_value(cdt, cdn, "field3", value3).then(() => {
            // Deep nesting
        });
    });
});
```

#### Missing Permission Checks
```python
# ❌ Bad: No permission check
@frappe.whitelist()
def update_document(name, data):
    doc = frappe.get_doc("Measurement Sheet", name)
    doc.update(data)
    doc.save()  # Security risk!
```

---

## Review Output Template

When documenting issues, use this format:

```markdown
### [Priority] Issue Title

**File**: `path/to/file.js` (line numbers)

**Problem**: Clear description of the issue

**Current Code**:
```javascript
// Show problematic code
```

**Refactored Version**:
```javascript
// Show improved code
```

**Explanation**: Why this change improves the code
```

---

## Additional Resources

- [Frappe Framework Documentation](https://frappeframework.com/docs)
- [Python PEP 8 Style Guide](https://pep8.org/)
- [JavaScript Best Practices](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

---

**Last Updated**: 2025-01-15  
**Version**: 1.0

