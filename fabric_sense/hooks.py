app_name = "fabric_sense"
app_title = "Fabric Sense"
app_publisher = "innogenio"
app_description = "An app for fabric sense"
app_email = "dona@gmail.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "fabric_sense",
# 		"logo": "/assets/fabric_sense/logo.png",
# 		"title": "Fabric Sense",
# 		"route": "/fabric_sense",
# 		"has_permission": "fabric_sense.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/fabric_sense/css/fabric_sense.css"
app_include_js = [
    "/assets/fabric_sense/js/helpers/tailoring_sheet_helpers.js",
    "/assets/fabric_sense/js/helpers/measurement_sheet_helpers.js",
]

# include js, css files in header of web template
# web_include_css = "/assets/fabric_sense/css/fabric_sense.css"
# web_include_js = "/assets/fabric_sense/js/fabric_sense.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "fabric_sense/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Item Price": "public/js/item_price.js",
    "Item": "public/js/item.js",
    "Sales Order": "public/js/sales_order.js",
    "Material Request": "public/js/material_request.js",
    "Payment Entry": "public/js/payment_entry.js",
    "Task": "public/js/task.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doc_events = {
    "Customer": {
        "before_save": "fabric_sense.fabric_sense.py.customer.generate_customer_code",
    },
    "Sales Order": {
        "validate": [
            "fabric_sense.fabric_sense.py.sales_order.validate_mbq",
            "fabric_sense.fabric_sense.py.sales_order.validate_billing_multiple",
        ],
        "on_update": "fabric_sense.fabric_sense.py.sales_order.send_customer_approval_notification",
    },
    "Material Request": {
        "validate": [
            "fabric_sense.fabric_sense.py.material_request.validate_stock_availability",
            "fabric_sense.fabric_sense.py.material_request.check_if_additional_request",
        ],
        "before_submit": "fabric_sense.fabric_sense.py.material_request.prevent_submission_without_approval",
    },
    "Purchase Order": {
        "on_submit": "fabric_sense.fabric_sense.py.purchase_order_notifications.send_vendor_po_notification",
    },
    "Sales Invoice": {
        "on_submit": "fabric_sense.fabric_sense.py.sales_invoice_notifications.send_customer_invoice_notification",
    },
    "Delivery Note": {
        "on_submit": [
            "fabric_sense.fabric_sense.py.delivery_note.send_customer_delivery_notification",
            "fabric_sense.fabric_sense.py.delivery_note.update_additional_material_request_status",
        ],
    },
    "Payment Entry": {
        "validate": "fabric_sense.fabric_sense.py.payment_entry.set_manager_approval_status_for_deductions",
        "on_submit": [
            "fabric_sense.fabric_sense.py.payment_entry.update_contractor_payment_history",
            "fabric_sense.fabric_sense.py.payment_entry_notifications.send_customer_payment_notification",
        ],
        "on_cancel": "fabric_sense.fabric_sense.py.payment_entry.revert_contractor_payment_history",
    },
    "Task": {
        "before_save": [
            "fabric_sense.fabric_sense.py.task.prefill_from_tailoring_sheet_and_service",
            "fabric_sense.fabric_sense.py.task.handle_status_change_to_working",
            "fabric_sense.fabric_sense.py.task.handle_status_change_to_completed",
            "fabric_sense.fabric_sense.py.task.notify_assigned_contractor",
        ],
        "on_update": [
            "fabric_sense.fabric_sense.py.task.create_contractor_payment_history"
        ],
    },
}
# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "fabric_sense/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "fabric_sense.utils.jinja_methods",
# 	"filters": "fabric_sense.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "fabric_sense.install.before_install"
# after_install = "fabric_sense.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "fabric_sense.uninstall.before_uninstall"
# after_uninstall = "fabric_sense.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "fabric_sense.utils.before_app_install"
# after_app_install = "fabric_sense.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "fabric_sense.utils.before_app_uninstall"
# after_app_uninstall = "fabric_sense.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "fabric_sense.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Item": "fabric_sense.fabric_sense.overrides.sku_generation.CustomItem"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"fabric_sense.tasks.all"
# 	],
# 	"daily": [
# 		"fabric_sense.tasks.daily"
# 	],
# 	"hourly": [
# 		"fabric_sense.tasks.hourly"
# 	],
# 	"weekly": [
# 		"fabric_sense.tasks.weekly"
# 	],
# 	"monthly": [
# 		"fabric_sense.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "fabric_sense.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "fabric_sense.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
    "Sales Order": "fabric_sense.fabric_sense.py.sales_order_dashboard.get_data",
    "Project": "fabric_sense.fabric_sense.py.project_dashboard.get_data",
    "Customer": "fabric_sense.fabric_sense.py.customer_dashboard.get_data",
}

fixtures = [
    {"dt": "Workspace", "filters": [["name", "in", ["Fabric Sense"]]]},
]

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["fabric_sense.utils.before_request"]
# after_request = ["fabric_sense.utils.after_request"]

# Job Events
# ----------
# before_job = ["fabric_sense.utils.before_job"]
# after_job = ["fabric_sense.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"fabric_sense.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
