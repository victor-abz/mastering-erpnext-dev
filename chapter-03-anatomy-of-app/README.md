# Chapter 3: Anatomy of an App

## 🎯 Learning Objectives

By the end of this chapter, you will understand:

- The structure of the `apps` folder and app directory breakdown
- Every hook in `hooks.py` and its specific purpose
- How `modules.txt` organizes your app into logical modules
- The patch system and how `patches.txt` manages database changes
- Using the `fixtures` folder for configuration export/import
- The role of `public` and `templates` directories for frontend assets

## 📚 Chapter Topics

### 3.1 The Apps Folder Structure

#### Standard App Directory Layout

```
apps/
└── my_custom_app/
    ├── my_custom_app/           # Main app package
    │   ├── __init__.py
    │   ├── hooks.py            # App hooks and configuration
    │   ├── modules.txt         # Module definitions
    │   ├── patches.txt         # Database patches
    │   ├── permissions.json    # Default permissions
    │   ├── setup.py            # Package setup
    │   ├── api.py              # Custom API endpoints
    │   ├── utils.py            # Utility functions
    │   ├── overrides.py        # Framework overrides
    │   ├── uninstall.py        # Cleanup on uninstall
    │   ├── my_custom_app/      # Main module
    │   │   ├── __init__.py
    │   │   ├── doctype/        # DocType definitions
    │   │   ├── page/           # Custom pages
    │   │   ├── report/         # Custom reports
    │   │   ├── dashboard_chart/ # Dashboard charts
    │   │   ├── data_migration/ # Data migration scripts
    │   │   ├── templates/      # Jinja templates
    │   │   └── web_template/   # Web templates
    │   ├── config/             # Configuration files
    │   │   └── desktop.json    # Desktop icons
    │   ├── public/             # Static assets
    │   │   ├── js/             # JavaScript files
    │   │   ├── css/            # CSS files
    │   │   ├── images/         # Images
    │   │   └── less/           # LESS stylesheets
    │   └── templates/          # Email/Jinja templates
    │       ├── emails/         # Email templates
    │       └── includes/       # Reusable templates
    ├── requirements.txt        # Python dependencies
    ├── package.json           # Node.js dependencies
    ├── yarn.lock              # Yarn lock file
    └── build.json             # Build configuration
```

#### Key Files Explained

**`__init__.py` (Root)**
```python
# App metadata
__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"
__description__ = "Custom ERPNext Application"

# App configuration
app_name = "my_custom_app"
app_title = "My Custom App"
app_publisher = "Your Company"
app_description = "A custom application for ERPNext"
app_icon = "octicon octicon-file-code"
app_color = "grey"
app_version = "1.0.0"
app_homepage = "https://github.com/your-username/my_custom_app"

# Included apps
includes_in_desktop = True

# Required apps (dependencies)
required_apps = ["frappe"]
```

### 3.2 hooks.py Explained

The `hooks.py` file is the central configuration point for your app. Every hook serves a specific purpose.

#### Document Hooks

```python
# Document events
doc_events = {
    "Sales Order": {
        "validate": "my_custom_app.sales_order.validate_sales_order",
        "on_submit": "my_custom_app.sales_order.on_submit_sales_order",
        "on_cancel": "my_custom_app.sales_order.on_cancel_sales_order",
        "on_update_after_submit": "my_custom_app.sales_order.update_related_docs"
    }
}

# Document permissions
permission_query_conditions = {
    "Sales Order": "my_custom_app.sales_order.get_permission_query_conditions",
    "Customer": "my_custom_app.customer.get_permission_query_conditions"
}

# Document permissions for specific roles
has_permission = {
    "Sales Order": "my_custom_app.sales_order.has_permission"
}
```

#### Scheduler Hooks

```python
# Scheduled events (cron-like)
scheduler_events = {
    "daily": [
        "my_custom_app.utils.daily_maintenance",
        "my_custom_app.reports.send_daily_reports"
    ],
    "weekly": [
        "my_custom_app.utils.weekly_cleanup"
    ],
    "monthly": [
        "my_custom_app.utils.monthly_archiving"
    ],
    "hourly": [
        "my_custom_app.utils.process_queue"
    ]
}
```

#### UI and Navigation Hooks

```python
# Add items to standard navigation bars
standard_navbar_items = [
    {
        "label": "Custom Tools",
        "url": "/custom-tools",
        "icon": "octicon octicon-tools"
    }
]

# Add items to desktop
app_include_js = "/assets/my_custom_app/js/app.js"
app_include_css = "/assets/my_custom_app/css/app.css"

# Customize desk
desk_js = {"items": ["my_custom_app/js/desk.js"]}
desk_css = {"items": ["my_custom_app/css/desk.css"]}

# Add custom buttons to forms
custom_script = {
    "Sales Order": "my_custom_app/public/js/sales_order.js"
}
```

#### API and Web Hooks

```python
# Whitelist Python methods for API access
whitelisted_methods = [
    "my_custom_app.api.get_custom_data",
    "my_custom_app.api.process_custom_request"
]

# Web routes
website_route_rules = [
    {"from_route": "/custom-page", "to_route": "my_custom_app.www.custom_page"},
    {"from_route": "/api/custom/<path:path>", "to_route": "my_custom_app.api.handle_request"}
]

# Website context
website_context = {
    "title": "My Custom App",
    "add_breadcrumbs": 1,
    "page_name": "custom_page"
}
```

#### Integration Hooks

```python
# Email templates
email_templates = {
    "custom_notification": {
        "subject": "Custom Notification",
        "response": "Custom notification sent successfully",
        "template": "templates/emails/custom_notification.html"
    }
}

# Data import/export
fixtures = [
    {"dt": "Custom Field", "filters": [["name", "like", "%custom%"]]},
    {"dt": "Property Setter", "filters": [["property", "=", "custom_property"]]}
]

# Boot script (runs on every page load)
boot_session = "my_custom_app.boot.set_session_data"
```

### 3.3 modules.txt Organization

The `modules.txt` file defines the modules within your app and their organization.

```txt
# Standard format
Module Name,Module Icon,Color,Label

# Examples
My Custom App,octicon octicon-package,green,My Custom App
Asset Management,octicon octicon-package,blue,Asset Management
Reports,octicon octicon-graph,orange,Reports
Settings,octicon octicon-gear,grey,Settings
```

#### Module Structure

Each module creates its own directory structure:

```
my_custom_app/
├── my_custom_app/
│   ├── __init__.py
│   ├── doctype/
│   ├── page/
│   └── report/
├── asset_management/
│   ├── __init__.py
│   ├── doctype/
│   ├── page/
│   └── report/
├── reports/
│   ├── __init__.py
│   └── report/
└── settings/
    ├── __init__.py
    └── page/
```

### 3.4 patches.txt and the Patch System

Patches manage database schema changes over time.

```txt
# Format: patch_version:description
2023-01-01:add_custom_fields.py:Add custom fields to Sales Order
2023-01-15:update_customer_data.py:Update customer data structure
2023-02-01:remove_deprecated_fields.py:Remove deprecated fields
```

#### Creating Patches

```python
# patches/2023-01-01/add_custom_fields.py

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    """Add custom fields to Sales Order"""
    
    custom_fields = {
        "Sales Order": [
            {
                "fieldname": "custom_priority",
                "label": "Priority",
                "fieldtype": "Select",
                "options": "Low\nMedium\nHigh",
                "insert_after": "customer",
                "depends_on": "eval:doc.docstatus == 0"
            },
            {
                "fieldname": "custom_notes",
                "label": "Custom Notes",
                "fieldtype": "Text Editor",
                "insert_after": "terms_and_conditions"
            }
        ]
    }
    
    create_custom_fields(custom_fields)
    frappe.db.commit()
```

### 3.5 Fixtures Folder

Fixtures allow you to export and import configuration data.

#### Common Fixture Types

```python
# fixtures/custom_fields.json
[
    {
        "doctype": "Custom Field",
        "name": "Sales Order-custom_priority",
        "dt": "Sales Order",
        "fieldname": "custom_priority",
        "label": "Priority",
        "fieldtype": "Select",
        "options": "Low\nMedium\nHigh",
        "insert_after": "customer"
    }
]

# fixtures/role_profiles.json
[
    {
        "doctype": "Role Profile",
        "name": "Custom Manager",
        "role": "Custom Manager",
        "roles": [
            {"role": "Sales Manager"},
            {"role": "Custom User"}
        ]
    }
]

# fixtures/property_setters.json
[
    {
        "doctype": "Property Setter",
        "name": "Sales Order-label-customer-Client",
        "doc_type": "Sales Order",
        "property": "label",
        "property_type": "Data",
        "value": "Client",
        "field_name": "customer"
    }
]
```

#### Exporting Fixtures

```bash
# Export specific DocTypes
bench --site dev.local export-fixtures

# Export all fixtures
bench --site dev.local export-fixtures --all

# Export specific fixtures
bench --site dev.local export-doc "Custom Field"
```

### 3.6 Public Directory

The `public` directory contains static assets served to the browser.

#### JavaScript Organization

```
public/
├── js/
│   ├── app.js              # App-wide JavaScript
│   ├── desk.js             # Desk-specific scripts
│   ├── forms/              # Form-specific scripts
│   │   ├── sales_order.js
│   │   └── customer.js
│   ├── utils/              # Utility functions
│   │   ├── helpers.js
│   │   └── validators.js
│   └── components/         # Reusable components
│       ├── custom_dialog.js
│       └── data_table.js
```

#### CSS Organization

```
public/
├── css/
│   ├── app.css             # App-wide styles
│   ├── desk.css            # Desk-specific styles
│   ├── forms/              # Form-specific styles
│   │   ├── sales_order.css
│   │   └── customer.css
│   ├── components/         # Component styles
│   └── print/              # Print format styles
```

### 3.7 Templates Directory

The `templates` directory contains Jinja templates for various purposes.

#### Email Templates

```html
<!-- templates/emails/custom_notification.html -->
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #333;">{{ subject }}</h2>
    
    <p>Hello {{ recipient_name }},</p>
    
    <p>{{ message }}</p>
    
    {% if doc %}
    <div style="background: #f5f5f5; padding: 15px; margin: 15px 0;">
        <h3>Document Details</h3>
        <p><strong>Document Type:</strong> {{ doc.doctype }}</p>
        <p><strong>Name:</strong> {{ doc.name }}</p>
        <p><strong>Status:</strong> {{ doc.status }}</p>
    </div>
    {% endif %}
    
    <p>Best regards,<br>{{ sender_name }}</p>
</div>
```

#### Web Templates

```html
<!-- templates/includes/custom_header.html -->
<header class="custom-header">
    <div class="container">
        <div class="logo">
            <img src="{{ app_logo }}" alt="{{ app_name }}">
        </div>
        <nav class="main-nav">
            <ul>
                <li><a href="/home">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/contact">Contact</a></li>
            </ul>
        </nav>
    </div>
</header>
```

## 🛠️ Practical Exercises

### Exercise 3.1: Create a Complete App Structure

1. Create a new app with proper structure
2. Set up `hooks.py` with various hooks
3. Create `modules.txt` with multiple modules
4. Add fixtures for configuration

### Exercise 3.2: Implement Hooks

1. Create document event handlers
2. Set up scheduled tasks
3. Add custom navigation items
4. Implement API endpoints

### Exercise 3.3: Manage Database Changes

1. Create a patch to add custom fields
2. Export and import fixtures
3. Test patch execution
4. Verify data integrity

## 🚀 Best Practices

### File Organization

- **Keep related files together** in module directories
- **Use descriptive naming** for files and functions
- **Separate concerns** between UI, business logic, and data access
- **Document your hooks** with comments explaining their purpose

### Hook Management

- **Minimize hook usage** to only necessary integrations
- **Use descriptive function names** for hook handlers
- **Handle errors gracefully** in hook functions
- **Test hooks thoroughly** in different scenarios

### Patch Management

- **Use semantic versioning** for patch naming
- **Write backward-compatible patches** when possible
- **Test patches on staging** before production
- **Document patch dependencies** and execution order

## 📖 Further Reading

- [Frappe App Development Guide](https://frappeframework.com/docs/user/en/development/app-development)
- [Hooks Reference](https://frappeframework.com/docs/user/en/development/hooks)
- [Patch System Documentation](https://frappeframework.com/docs/user/en/development/patch-system)

## 🎯 Chapter Summary

Understanding app anatomy is crucial for effective Frappe development:

- **Structure matters** - Organize files logically within modules
- **Hooks are powerful** - Use them to integrate with the framework
- **Patches manage change** - Keep database schema evolution under control
- **Fixtures enable configuration** - Export and import settings easily
- **Assets complete the experience** - JavaScript, CSS, and templates enhance UX

---

**Next Chapter**: Advanced DocType design and metadata management.
