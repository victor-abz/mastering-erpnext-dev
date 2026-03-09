# -*- coding: utf-8 -*-
"""
My Custom App - Hooks Configuration
Chapter 3: Anatomy of an App

This file demonstrates all available hooks and their usage
in a Frappe application.
"""

# =============================================================================
# DOCUMENT HOOKS
# =============================================================================

# Document events - triggered during document lifecycle
doc_events = {
    "User": {
        "validate": "my_custom_app.user_events.validate_user",
        "on_update": "my_custom_app.user_events.on_user_update",
        "after_insert": "my_custom_app.user_events.after_user_insert"
    },
    "ToDo": {
        "validate": "my_custom_app.todo_events.validate_todo",
        "on_submit": "my_custom_app.todo_events.on_todo_submit",
        "on_cancel": "my_custom_app.todo_events.on_todo_cancel"
    }
}

# Permission query conditions - filter what users can see
permission_query_conditions = {
    "ToDo": "my_custom_app.permissions.get_todo_permission_conditions",
    "User": "my_custom_app.permissions.get_user_permission_conditions"
}

# Has permission - fine-grained permission control
has_permission = {
    "ToDo": "my_custom_app.permissions.has_todo_permission",
    "User": "my_custom_app.permissions.has_user_permission"
}

# =============================================================================
# SCHEDULER HOOKS
# =============================================================================

# Scheduled events - cron-like task scheduling
scheduler_events = {
    "daily": [
        "my_custom_app.tasks.daily_cleanup",
        "my_custom_app.tasks.send_daily_summary",
        "my_custom_app.tasks.archive_old_records"
    ],
    "weekly": [
        "my_custom_app.tasks.weekly_maintenance",
        "my_custom_app.tasks.generate_weekly_report"
    ],
    "monthly": [
        "my_custom_app.tasks.monthly_archiving",
        "my_custom_app.tasks.generate_monthly_report"
    ],
    "hourly": [
        "my_custom_app.tasks.process_queue",
        "my_custom_app.tasks.update_statistics"
    ],
    "cron": {
        "0 2 * * *": ["my_custom_app.tasks.nightly_backup"],  # Daily at 2 AM
        "0 */6 * * *": ["my_custom_app.tasks.sync_external_data"]  # Every 6 hours
    }
}

# =============================================================================
# UI AND NAVIGATION HOOKS
# =============================================================================

# Standard navbar items - add to main navigation
standard_navbar_items = [
    {
        "label": "Custom Tools",
        "url": "/custom-tools",
        "icon": "octicon octicon-tools",
        "target": "_blank"
    },
    {
        "label": "Help Center",
        "url": "/help",
        "icon": "octicon octicon-question"
    }
]

# App includes - global JavaScript and CSS
app_include_js = "/assets/my_custom_app/js/app.js"
app_include_css = "/assets/my_custom_app/css/app.css"

# Desk customization
desk_js = {"items": ["my_custom_app/js/desk.js"]}
desk_css = {"items": ["my_custom_app/css/desk.css"]}

# Custom scripts for specific DocTypes
custom_script = {
    "User": "my_custom_app/public/js/user.js",
    "ToDo": "my_custom_app/public/js/todo.js",
    "Sales Order": "my_custom_app/public/js/sales_order.js"
}

# Override standard templates
override_doctype_class = {
    "User": "my_custom_app.overrides.CustomUser",
    "ToDo": "my_custom_app.overrides.CustomToDo"
}

# =============================================================================
# API AND WEB HOOKS
# =============================================================================

# Whitelisted methods - accessible via REST API
whitelisted_methods = [
    "my_custom_app.api.get_user_statistics",
    "my_custom_app.api.get_todo_list",
    "my_custom_app.api.process_custom_request",
    "my_custom_app.api.generate_report"
]

# Website route rules - custom URL routing
website_route_rules = [
    {
        "from_route": "/custom-tools",
        "to_route": "my_custom_app.www.custom_tools.index"
    },
    {
        "from_route": "/help",
        "to_route": "my_custom_app.www.help.index"
    },
    {
        "from_route": "/api/custom/<path:path>",
        "to_route": "my_custom_app.api.handle_request"
    }
]

# Website context - global variables for web pages
website_context = {
    "title": "My Custom App",
    "add_breadcrumbs": 1,
    "page_name": "custom_page",
    "show_sidebar": True,
    "custom_css": "/assets/my_custom_app/css/website.css"
}

# Website generators - dynamic page generation
website_generators = {
    "Custom Page": "my_custom_app.website.generate_custom_page"
}

# =============================================================================
# INTEGRATION HOOKS
# =============================================================================

# Email templates
email_templates = {
    "custom_notification": {
        "subject": "Custom Notification from My App",
        "response": "Custom notification sent successfully",
        "template": "templates/emails/custom_notification.html"
    },
    "daily_summary": {
        "subject": "Daily Summary Report",
        "response": "Daily summary sent successfully",
        "template": "templates/emails/daily_summary.html"
    }
}

# Data fixtures - export/import configuration
fixtures = [
    {"dt": "Custom Field", "filters": [["name", "like", "%custom_%"]]},
    {"dt": "Property Setter", "filters": [["property", "=", "custom_property"]]},
    {"dt": "Role Profile", "filters": [["name", "like", "Custom%"]}},
    {"dt": "Custom Script", "filters": [["name", "like", "%custom%"]]}
]

# Boot script - runs on every page load
boot_session = "my_custom_app.boot.set_session_data"

# =============================================================================
# REPORTING AND DASHBOARD HOOKS
# =============================================================================

# Standard reports
standard_reports = [
    {
        "label": "Custom User Report",
        "name": "Custom User Report",
        "doctype": "User",
        "ref_doctype": "User",
        "report_name": "Custom User Report",
        "report_type": "Script Report",
        "is_standard": "Yes"
    }
]

# Query reports
query_reports = [
    {
        "label": "Custom Todo Query",
        "name": "Custom Todo Query",
        "ref_doctype": "ToDo",
        "report_name": "Custom Todo Query"
    }
]

# =============================================================================
# CUSTOMIZATION HOOKS
# =============================================================================

# Extend standard forms
extend_doctype_class = {
    "User": "my_custom_app.overrides.CustomUser",
    "ToDo": "my_custom_app.overrides.CustomToDo"
}

# Override standard methods
override_doctype_class = {
    "User": "my_custom_app.overrides.CustomUser"
}

# Standard templates
standard_templates = {
    "templates/includes/custom_header.html": "my_custom_app.templates.includes.custom_header",
    "templates/includes/custom_footer.html": "my_custom_app.templates.includes.custom_footer"
}

# =============================================================================
# NOTIFICATION HOOKS
# =============================================================================

# Notification templates
notification_templates = {
    "Custom Notification": {
        "for_user": True,
        "subject": "Custom Notification",
        "template": "my_custom_app.notifications.custom_notification"
    }
}

# =============================================================================
# SEARCH HOOKS
# =============================================================================

# Global search scope
global_search_scope = {
    "Custom DocType": ["my_custom_app.custom_doctype.CustomDocType"]
}

# =============================================================================
# DATA MIGRATION HOOKS
# =============================================================================

# Data migration classes
data_migration_classes = {
    "Custom Data": "my_custom_app.migration.CustomDataMigration"
}

# =============================================================================
# TESTING HOOKS
# =============================================================================

# Test dependencies
test_dependencies = ["frappe"]

# Test fixtures
test_fixtures = ["User", "ToDo", "Custom DocType"]

# =============================================================================
# DEVELOPMENT HOOKS
# =============================================================================

# Developer mode hooks
if frappe.conf.developer_mode:
    # Add development-specific includes
    app_include_js += "," + "/assets/my_custom_app/js/dev.js"
    
    # Add development routes
    website_route_rules.extend([
        {
            "from_route": "/dev-tools",
            "to_route": "my_custom_app.www.dev_tools.index"
        }
    ])

# =============================================================================
# CONDITIONAL HOOKS
# =============================================================================

# Add hooks only if specific apps are installed
if "erpnext" in frappe.get_installed_apps():
    # ERPNext-specific hooks
    doc_events.update({
        "Sales Order": {
            "validate": "my_custom_app.erpnext_hooks.validate_sales_order",
            "on_submit": "my_custom_app.erpnext_hooks.on_sales_order_submit"
        }
    })
    
    standard_reports.extend([
        {
            "label": "Custom Sales Report",
            "name": "Custom Sales Report",
            "doctype": "Sales Order",
            "ref_doctype": "Sales Order",
            "report_name": "Custom Sales Report",
            "report_type": "Script Report",
            "is_standard": "Yes"
        }
    ])

# =============================================================================
# UTILITY HOOKS
# =============================================================================

# Translation files
translation_files = [
    "translations/my_custom_app.csv",
    "translations/my_custom_app_ar.csv"  # Arabic
]

# Custom error handlers
error_handlers = {
    "my_custom_app.exceptions.CustomException": "my_custom_app.exceptions.handle_custom_exception"
}

# =============================================================================
# PERFORMANCE HOOKS
# =============================================================================

# Cache invalidation
cache_clear_events = {
    "User": ["my_custom_app.cache.clear_user_cache"],
    "ToDo": ["my_custom_app.cache.clear_todo_cache"]
}

# =============================================================================
# SECURITY HOOKS
# =============================================================================

# Rate limiting
rate_limit_endpoints = {
    "my_custom_app.api.process_custom_request": {
        "limit": 100,
        "window": 3600  # 100 requests per hour
    }
}

# =============================================================================
# LOGGING HOOKS
# =============================================================================

# Custom loggers
loggers = {
    "my_custom_app": {
        "handler": "file",
        "level": "INFO",
        "file_name": "my_custom_app.log"
    }
}

# =============================================================================
# MAINTENANCE HOOKS
# =============================================================================

# App uninstall cleanup
app_uninstall_hooks = [
    "my_custom_app.uninstall.cleanup_custom_data",
    "my_custom_app.uninstall.remove_custom_files"
]

# App update hooks
app_update_hooks = [
    "my_custom_app.update.update_app_data",
    "my_custom_app.update.migrate_app_settings"
]
