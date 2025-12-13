# Lead, Customer, and Project Creation Guidelines

## Overview

This guide covers the creation and customization of Leads, Customers, and Projects in the Fabric Sense application. We utilize ERPNext's default doctypes which provide robust functionality and can be customized to meet specific business requirements.

---

## Lead and Customer Management

### Using Default Doctypes

ERPNext's standard **Lead** and **Customer** doctypes are sufficient for most requirements in the fabric manufacturing workflow:

- **Lead Doctype**: Captures potential customer information, contact details, and lead source
- **Customer Doctype**: Manages customer master data, billing information, and customer-specific settings
- **Project Doctype**: Manage project-based work and can be effectively used for fabric manufacturing projects

### Customizing Lead , Customer and Project Doctypes

If you need to add new fields or modify existing properties, you can customize these default doctypes without modifying the core ERPNext code.

#### Steps to Customize a Doctype

1. **Open Customize Form View**
   - Navigate to the doctype's List View (e.g., Lead List or Customer List)
   - Click on the **Menu** dropdown (three dots icon)
   - Select the **Customize** option
   - This opens the Customize Form view for the selected doctype

2. **Add or Modify Fields**
   - In the Customize Form view, you can:
     - Add new custom fields by clicking **Add Row** in the Fields table
     - Modify existing field properties (label, field type, mandatory, read-only, etc.)
     - Rearrange field order using drag-and-drop
     - Add field dependencies and validation rules
   - Configure field properties as needed:
     - **Label**: Display name of the field
     - **Field Type**: Data type (Data, Select, Link, Text, etc.)
     - **Options**: For Select or Link fields
     - **Mandatory**: Whether the field is required
     - **Read Only**: Whether the field can be edited
     - **Hidden**: Whether the field is visible

3. **Save Changes**
   - Click the **Save** button to apply your customizations
   - The changes will be immediately reflected in the doctype forms

4. **Export Customizations**
   - After saving, click on the **Actions** menu (dropdown button)
   - Select **Export Customizations**
   - Choose the module where the customizations should be exported (e.g., `fabric_sense`)
   - Click **Submit**
   - The customizations will be exported as JSON files in your app directory
   - These files will be available in VS Code under: `fabric_sense/fabric_sense/custom/`

#### Benefits of Exporting Customizations

- **Version Control**: Customizations are stored as code and can be tracked in Git
- **Portability**: Easy to migrate customizations across different environments
- **Team Collaboration**: Other developers can see and review customizations
- **Deployment**: Customizations can be deployed to production using bench commands

### Converting Lead to Customer

ERPNext provides a built-in workflow to convert qualified leads into customers.

#### Conversion Process

1. **Open Lead Form**
   - Navigate to the Lead you want to convert
   - Open the Lead document

2. **Create Customer**
   - Click on the **Create** button in the top-right corner
   - Select **Customer** from the dropdown menu
   - ERPNext will automatically create a new Customer with data populated from the Lead

3. **Review and Save**
   - Review the auto-populated customer information
   - Add any additional required fields
   - Save the Customer document

4. **Lead Status Update**
   - Once converted, the Lead status is automatically updated to "Converted"

#### Additional Conversion Options

From the Lead form's **Create** menu, you can also create:
- **Opportunity**: To track potential sales deals
- **Quotation**: To provide price quotes directly from the lead
- **Prospect**: For B2B scenarios with multiple contacts

---

## Project Management

### Using Default Project Doctype

ERPNext's **Project** doctype is designed to manage project-based work and can be effectively used for fabric manufacturing projects. It includes:

- Project timeline and milestone tracking
- Task management and assignment
- Cost tracking and budgeting
- Project status monitoring
- Integration with Sales Orders and other documents

### Customizing Project Doctype

Similar to Lead and Customer, the Project doctype can be customized to align with fabric manufacturing requirements.

#### Steps to Customize Project Doctype

1. **Open Customize Form View**
   - Navigate to **Project List**
   - Click on the **Menu** dropdown (three dots icon)
   - Select the **Customize** option

2. **Add or Modify Fields**
   - Add custom fields specific to fabric manufacturing:
     - Fabric specifications
     - Production stages
     - Quality checkpoints
     - Machine allocation
     - Raw material requirements
   - Modify existing field properties as needed

3. **Save and Export Customizations**
   - Click **Save** to apply changes
   - Go to **Actions** → **Export Customizations**
   - Select the `fabric_sense` module
   - Click **Submit**
   - Customizations will be available in VS Code under `fabric_sense/fabric_sense/custom/`

### Creating Projects

1. **Navigate to Project List**
   - Go to **Projects** → **Project**
   - Click **New**

2. **Fill Project Details**
   - **Project Name**: Enter a descriptive name
   - **Customer**: Link to the customer
   - **Sales Order**: Optionally link to a Sales Order
   - **Expected Start Date**: Set project start date
   - **Expected End Date**: Set project completion date
   - **Project Type**: Select appropriate type (e.g., Internal, External)
   - **Status**: Set initial status (e.g., Open)

3. **Add Project Tasks**
   - In the **Tasks** section, add individual tasks
   - Assign tasks to team members
   - Set task dependencies and priorities
   - Define task start and end dates

4. **Set Budget and Costs**
   - Configure project budget if applicable
   - Track actual costs against budget

5. **Save Project**
   - Click **Save** to create the project

---

## Adding Custom JavaScript to Default Doctypes

To add extra JavaScript functionality to ERPNext's default doctypes (Lead, Customer, Project, etc.), you can create custom JS files in your app and link them through the `hooks.py` file.

### Steps to Add Custom JavaScript

#### 1. Create JavaScript File

Create a JS file in your app's public folder:

```bash
fabric_sense/public/js/lead.js
```

Example JavaScript code for Lead doctype:

```javascript
frappe.ui.form.on('Lead', {
    refresh: function(frm) {
        // Add custom button
        frm.add_custom_button(__('Custom Action'), function() {
            frappe.msgprint(__('Custom button clicked!'));
        });
    },
    
    onload: function(frm) {
        // Custom logic when form loads
        console.log('Lead form loaded');
    },
    
    custom_field: function(frm) {
        // Trigger when custom_field value changes
        if (frm.doc.custom_field) {
            // Perform custom logic
            frm.set_value('another_field', 'Auto-populated value');
        }
    },
    
    validate: function(frm) {
        // Custom validation before saving
        if (frm.doc.custom_fabric_type_interest && !frm.doc.expected_closing) {
            frappe.msgprint(__('Please set expected closing date'));
            frappe.validated = false;
        }
    }
});
```

#### 2. Link JavaScript in hooks.py

Open the `hooks.py` file in your app:

```bash
fabric_sense/hooks.py
```

Add the doctype_js configuration:

```python
# Document Events
# ---------------
# Hook on document methods and events

doctype_js = {
    "Lead": "public/js/lead.js",
    "Customer": "public/js/customer.js",
    "Project": "public/js/project.js"
}
```

#### 3. Build and Restart

After adding the JavaScript files and updating hooks.py:

```bash
# Build the app to include new JS files
bench build --app fabric_sense

# Clear cache
bench clear-cache

# Restart bench (if needed)
bench restart
```

#### 4. Verify JavaScript is Loaded

- Open the doctype form in the browser
- Open browser Developer Tools (F12)
- Check the Console for any errors
- Test your custom functionality

### Common JavaScript Customizations

#### Fetch Data from Another Doctype

```javascript
frappe.ui.form.on('Project', {
    customer: function(frm) {
        if (frm.doc.customer) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Customer',
                    name: frm.doc.customer
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('custom_quality_standards', r.message.custom_quality_standards);
                    }
                }
            });
        }
    }
});
```

#### Add Custom Filters to Link Fields

```javascript
frappe.ui.form.on('Lead', {
    refresh: function(frm) {
        frm.set_query('custom_fabric_type', function() {
            return {
                filters: {
                    'is_active': 1,
                    'category': 'Premium'
                }
            };
        });
    }
});
```

---

## Overriding Default Logic of ERPNext Doctypes

To override or extend the default server-side logic of ERPNext doctypes, you can use Python hooks and custom methods.

### 1: Using Document Events in hooks.py

Document events allow you to hook into the lifecycle of a document without modifying the core code.

#### Available Document Events

- `before_insert`: Before a new document is inserted
- `after_insert`: After a new document is inserted
- `before_save`: Before a document is saved
- `after_save`: After a document is saved
- `before_submit`: Before a document is submitted
- `after_submit`: After a document is submitted
- `before_cancel`: Before a document is cancelled
- `after_cancel`: After a document is cancelled
- `before_delete`: Before a document is deleted
- `after_delete`: After a document is deleted
- `on_update`: When a document is updated
- `on_trash`: When a document is moved to trash

#### Steps to Override Using Document Events

**1. Create a Python file for custom logic:**

```bash
fabric_sense/fabric_sense/custom_methods/lead_custom.py
```

Example code:

```python
import frappe
from frappe import _

def validate_lead(doc, method):
    """Custom validation for Lead doctype"""
    if doc.custom_fabric_type_interest and not doc.custom_expected_order_volume:
        frappe.throw(_("Expected Order Volume is mandatory when Fabric Type Interest is selected"))

def after_insert_lead(doc, method):
    """Custom logic after Lead is created"""
    # Send notification to sales team
    frappe.sendmail(
        recipients=['sales@example.com'],
        subject=f'New Lead Created: {doc.name}',
        message=f'A new lead {doc.lead_name} has been created.'
    )

def before_save_customer(doc, method):
    """Custom logic before Customer is saved"""
    # Auto-set customer group based on territory
    if doc.territory == 'Export':
        doc.customer_group = 'Export Customers'
    elif doc.territory == 'Local':
        doc.customer_group = 'Domestic Customers'

def on_submit_project(doc, method):
    """Custom logic when Project is submitted"""
    # Create initial tasks automatically
    create_default_project_tasks(doc)

def create_default_project_tasks(project):
    """Helper function to create default tasks"""
    default_tasks = [
        {'subject': 'Material Procurement', 'priority': 'High'},
        {'subject': 'Production Planning', 'priority': 'High'},
        {'subject': 'Quality Check', 'priority': 'Medium'},
        {'subject': 'Packaging', 'priority': 'Low'}
    ]
    
    for task_data in default_tasks:
        task = frappe.get_doc({
            'doctype': 'Task',
            'project': project.name,
            'subject': task_data['subject'],
            'priority': task_data['priority']
        })
        task.insert()
```

**2. Register events in hooks.py:**

```python
# Document Events
doc_events = {
    "Lead": {
        "validate": "fabric_sense.fabric_sense.custom_methods.lead_custom.validate_lead",
        "after_insert": "fabric_sense.fabric_sense.custom_methods.lead_custom.after_insert_lead"
    },
    "Customer": {
        "before_save": "fabric_sense.fabric_sense.custom_methods.lead_custom.before_save_customer"
    },
    "Project": {
        "on_submit": "fabric_sense.fabric_sense.custom_methods.lead_custom.on_submit_project"
    }
}
```

**3. Restart bench to apply changes:**

```bash
bench restart
```

-----

## Troubleshooting

### Customizations Not Appearing in VS Code

- Ensure you selected the correct module during export
- Check the `fabric_sense/fabric_sense/custom/` directory
- Verify file permissions in the app directory

### Customizations Not Syncing to Other Sites

- Export customizations from the source site
- Commit the JSON files to version control
- Run `bench migrate` on the target site to apply customizations

### Field Validation Errors

- Check field dependencies and validation rules
- Ensure mandatory fields have default values or are filled
- Review field type compatibility with existing data

### Custom JavaScript Not Loading

- Verify the JS file path in `hooks.py` is correct
- Run `bench build --app fabric_sense` to rebuild assets
- Clear browser cache and hard refresh (Ctrl+Shift+R)
- Check browser console for JavaScript errors
- Ensure the JS file exists in the correct location

### Document Events Not Triggering

- Verify the method path in `doc_events` is correct
- Check that the Python file and function exist
- Restart bench after modifying `hooks.py`
- Check error logs: `bench logs` or `tail -f sites/[site-name]/logs/error.log`
- Ensure the function signature is correct: `def function_name(doc, method)`


---

## Additional Resources

### ERPNext Documentation
- [ERPNext Lead Documentation](https://docs.erpnext.com/docs/user/manual/en/CRM/lead)
- [ERPNext Customer Documentation](https://docs.erpnext.com/docs/user/manual/en/CRM/customer)
- [ERPNext Project Documentation](https://docs.erpnext.com/docs/user/manual/en/projects/project)

### Frappe Framework Documentation
- [Frappe Customize Form Guide](https://frappeframework.com/docs/user/en/desk/customize-form)
- [Frappe Client-side Scripting](https://frappeframework.com/docs/user/en/desk/scripting)
- [Frappe Document Events](https://frappeframework.com/docs/user/en/api/document)
- [Frappe Hooks](https://frappeframework.com/docs/user/en/python/hooks)
- [Frappe Controller Methods](https://frappeframework.com/docs/user/en/api/document)

---

**Note**: Always test customizations in a development environment before applying them to production systems.
