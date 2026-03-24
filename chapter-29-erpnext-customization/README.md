# Chapter 29: ERPNext Customization — The Complete Guide

## Overview

Customization in ERPNext means modifying the system to meet specific business requirements — from simple field additions to complex behavioral overrides. The golden rule: **never touch the core**. Always create a new app to hold your customizations.

**Customization vs. Configuration vs. Development:**
- **Configuration**: Setting up existing features (e.g., setting tax rates)
- **Customization**: Modifying existing behavior (e.g., adding fields, changing workflows)
- **Development**: Building new features from scratch (e.g., new DocTypes, new apps)

---

## 1. Custom Fields

Custom Fields add new fields to existing DocTypes without modifying core code. They are stored in `tabCustom Field` and merged with DocType metadata at runtime.

### Creating via UI

Navigate to **Customize Form** → Select DocType → Add Field

### Creating Programmatically

```python
import frappe

# Create a custom field
custom_field = frappe.get_doc({
    "doctype": "Custom Field",
    "dt": "Customer",
    "fieldname": "custom_tax_id",
    "label": "Tax ID",
    "fieldtype": "Data",
    "insert_after": "customer_name",
    "reqd": 0,
    "in_list_view": 1,
})
custom_field.insert()
frappe.db.commit()
```

### Exporting as Fixtures

```python
# In hooks.py
fixtures = [
    "Custom Field",
    "Property Setter",
    {"dt": "Custom Field", "filters": [["module", "=", "My App"]]},
]
```

```bash
bench export-fixtures
# Creates: apps/myapp/myapp/fixtures/custom_field.json
```

---

## 2. Property Setters

Property Setters override properties of standard DocTypes and fields without modifying core code. Changes survive framework updates.

```python
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

# Make a field mandatory
make_property_setter(
    doctype="Customer",
    fieldname="customer_name",
    property="reqd",
    value="1",
    property_type="Check"
)

# Hide a field
make_property_setter(
    doctype="Sales Order",
    fieldname="tc_name",
    property="hidden",
    value="1",
    property_type="Check"
)

# Change field label
make_property_setter(
    doctype="Customer",
    fieldname="customer_name",
    property="label",
    value="Company Name",
    property_type="Data"
)
```

**Common Properties:**
- `reqd` — Make field mandatory
- `hidden` — Hide field
- `read_only` — Make field read-only
- `label` — Change field label
- `default` — Set default value
- `options` — Change select options
- `allow_on_submit` — Allow editing after submit

---

## 3. Fixtures

Fixtures are predefined data records bundled with an app for consistent setup across environments.

```python
# hooks.py
fixtures = [
    "Custom Field",
    "Property Setter",
    "Client Script",
    {"dt": "Role", "filters": [["name", "in", ["Custom Role 1", "Custom Role 2"]]]},
    {"dt": "Print Format", "filters": [["module", "=", "My App"]]},
    {"dt": "Workflow", "filters": [["document_type", "=", "Leave Application"]]},
]
```

```bash
# Export fixtures
bench export-fixtures

# Fixtures auto-install when app is installed
bench --site mysite install-app myapp
```

**Example fixture file** (`fixtures/custom_field.json`):
```json
[
    {
        "doctype": "Custom Field",
        "dt": "Customer",
        "fieldname": "custom_loyalty_tier",
        "label": "Loyalty Tier",
        "fieldtype": "Select",
        "options": "Bronze\nSilver\nGold\nPlatinum",
        "insert_after": "customer_name"
    }
]
```

---

## 4. Frappe Hooks Deep Dive

The `hooks.py` file is the contract between your app and the Frappe framework. It defines how and when your app participates in system events.

```python
# hooks.py — comprehensive example

# Document Events
doc_events = {
    "Sales Order": {
        "before_save": "myapp.custom.validate_sales_order",
        "on_submit": "myapp.custom.create_delivery_note",
        "on_cancel": "myapp.custom.reverse_stock",
        "after_insert": "myapp.custom.notify_manager",
    },
    "Customer": {
        "after_insert": "myapp.custom.setup_customer_defaults",
    },
    "*": {
        "on_trash": "myapp.custom.log_deletion",
    }
}

# Scheduler Events
scheduler_events = {
    "all": ["myapp.tasks.every_minute"],
    "hourly": ["myapp.tasks.sync_inventory"],
    "daily": ["myapp.tasks.send_daily_report"],
    "weekly": ["myapp.tasks.weekly_cleanup"],
    "monthly": ["myapp.tasks.monthly_summary"],
    "cron": {
        "0 2 * * *": ["myapp.tasks.midnight_backup"],
        "*/15 * * * *": ["myapp.tasks.every_15_minutes"],
    }
}

# Override Whitelisted Methods
override_whitelisted_methods = {
    "frappe.client.get": "myapp.api.custom_get",
    "erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry": 
        "myapp.overrides.custom_payment_entry",
}

# Override DocType Classes
override_doctype_class = {
    "Sales Order": "myapp.overrides.CustomSalesOrder",
    "Customer": "myapp.overrides.CustomCustomer",
}

# Permission Hooks
has_permission = {
    "Sales Order": "myapp.permissions.sales_order_permission",
}

permission_query_conditions = {
    "Sales Order": "myapp.permissions.get_permission_query_conditions",
}

# Include JS/CSS
app_include_js = ["/assets/myapp/js/custom.js"]
app_include_css = ["/assets/myapp/css/custom.css"]

# DocType-specific JS
doctype_js = {
    "Sales Order": "public/js/sales_order.js",
    "Customer": "public/js/customer.js",
}

doctype_list_js = {
    "Sales Order": "public/js/sales_order_list.js",
}

# Session Hooks
on_login = "myapp.auth.on_login"
on_logout = "myapp.auth.on_logout"
on_session_creation = "myapp.auth.on_session_creation"

# Boot Session (data sent to client on login)
# Note: boot_session is NOT a valid hook name — use extend_bootinfo instead
extend_bootinfo = "myapp.boot.boot_session"

# Installation
after_install = "myapp.setup.after_install"
after_migrate = "myapp.setup.after_migrate"
before_migrate = "myapp.setup.before_migrate"
```

---

## 5. Override DocType Classes (Monkey Patching via hooks)

```python
# myapp/overrides.py
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

class CustomSalesOrder(SalesOrder):
    def validate(self):
        super().validate()
        self.custom_validation()

    def custom_validation(self):
        if self.grand_total > 1000000:
            frappe.throw("Orders above 1M require special approval")

    def on_submit(self):
        super().on_submit()
        self.notify_warehouse()

    def notify_warehouse(self):
        frappe.sendmail(
            recipients=["warehouse@company.com"],
            subject=f"New Order: {self.name}",
            message=f"Order {self.name} submitted for {self.customer}"
        )
```

```python
# hooks.py
override_doctype_class = {
    "Sales Order": "myapp.overrides.CustomSalesOrder",
}
```

---

## 6. Permission Hooks

```python
# myapp/permissions.py
import frappe

def sales_order_permission(doc, ptype, user):
    """Custom permission logic for Sales Orders"""
    # Sales Manager can only see orders from their territory
    if "Sales Manager" in frappe.get_roles(user):
        user_territory = frappe.db.get_value("User", user, "territory")
        if doc and doc.territory != user_territory:
            return False
    return True

def get_permission_query_conditions(user):
    """Add conditions to list queries"""
    if "Sales Manager" in frappe.get_roles(user):
        user_territory = frappe.db.get_value("User", user, "territory")
        return f"`tabSales Order`.territory = '{user_territory}'"
    return ""
```

```python
# hooks.py
has_permission = {
    "Sales Order": "myapp.permissions.sales_order_permission",
}

permission_query_conditions = {
    "Sales Order": "myapp.permissions.get_permission_query_conditions",
}
```

---

## 7. Script Reports (Frappe Script Report Boilerplate)

Script Reports give you full Python control over report data.

```python
# myapp/report/my_report/my_report.py

import frappe
from frappe import _

def execute(filters=None):
    """Main entry point for script report"""
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200,
        },
        {
            "label": _("Total Orders"),
            "fieldname": "total_orders",
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "label": _("Total Amount"),
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 150,
        },
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    return frappe.db.sql(f"""
        SELECT
            customer,
            COUNT(*) as total_orders,
            SUM(grand_total) as total_amount
        FROM `tabSales Order`
        WHERE docstatus = 1
            {conditions}
        GROUP BY customer
        ORDER BY total_amount DESC
    """, filters, as_dict=True)

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += " AND posting_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND posting_date <= %(to_date)s"
    if filters.get("customer"):
        conditions += " AND customer = %(customer)s"
    return conditions
```

---

## 8. Frappe Field Types Reference

| Field Type | DB Type | Use Case |
|---|---|---|
| Data | VARCHAR(140) | Short text, names, codes |
| Text | TEXT | Medium text, descriptions |
| Long Text | LONGTEXT | Long content, HTML |
| Small Text | TEXT | Short paragraphs |
| Int | INT | Whole numbers |
| Float | DECIMAL | Decimal numbers |
| Currency | DECIMAL | Money values |
| Percent | DECIMAL | Percentages |
| Check | INT(1) | Boolean yes/no |
| Date | DATE | Date only |
| Datetime | DATETIME | Date and time |
| Time | TIME | Time only |
| Link | VARCHAR(140) | Reference to another DocType |
| Dynamic Link | VARCHAR(140) | Reference to any DocType |
| Select | VARCHAR(140) | Dropdown options |
| Table | — | Child table |
| Table MultiSelect | — | Multi-select child table |
| Attach | TEXT | File attachment |
| Attach Image | TEXT | Image attachment |
| HTML | LONGTEXT | HTML content |
| Code | LONGTEXT | Code editor |
| Markdown Editor | LONGTEXT | Markdown content |
| Color | VARCHAR(140) | Color picker |
| Rating | DECIMAL | Star rating |
| Geolocation | LONGTEXT | Map coordinates |
| Signature | LONGTEXT | Signature pad |
| Password | TEXT | Encrypted password |
| Read Only | — | Display only |
| Section Break | — | UI section divider |
| Column Break | — | UI column divider |
| Tab Break | — | UI tab divider |
| Fold | — | Collapsible section |
| Heading | — | Section heading |
| HTML Editor | LONGTEXT | Rich text editor |
| JSON | LONGTEXT | JSON data |
| Autocomplete | VARCHAR(140) | Autocomplete input |

**Important:** `Data` fields use VARCHAR(140) which counts toward the 65KB MySQL row size limit. Use `Text` for descriptions and notes to save row space (TEXT only uses 10 bytes in-row vs 140+ for VARCHAR).

---

## 9. DocType Namespacing

When creating custom DocTypes, use proper namespacing to avoid conflicts:

```python
# Bad: Generic names that may conflict
class Item(Document): pass
class Order(Document): pass

# Good: Namespaced names
class MyAppItem(Document): pass
class MyAppSalesOrder(Document): pass
```

**Naming conventions:**
- DocType names: `{App Name} {Entity}` → `"HR Leave Request"`, `"Asset Maintenance Log"`
- Module names: lowercase with underscores → `hr`, `asset_management`
- App names: lowercase with underscores → `my_custom_app`

---

## 10. Custom vs Standard DocTypes

| Aspect | Standard DocType | Custom DocType |
|---|---|---|
| Location | Core app (frappe/erpnext) | Your custom app |
| Modification | Via Property Setter, Custom Fields | Direct editing |
| Upgrade safety | Preserved on upgrade | Preserved (it's yours) |
| Best for | Extending existing entities | New business entities |

**When to use Custom Fields vs new DocType:**
- **Custom Fields**: Adding data to existing entities (Customer, Sales Order)
- **New DocType**: Entirely new business entity (Asset, Training Record, Vendor Rating)

---

## 11. Interview Questions & Key Concepts

### What is the difference between a DocType and a Document?
- **DocType**: The schema/blueprint (like a class definition)
- **Document**: An instance of a DocType (like an object instance)

### What is the Singles table?
Single DocTypes (like System Settings) store their data in `tabSingles` as key-value pairs instead of having their own table. Access with `frappe.db.get_single_value("System Settings", "field_name")`.

### How does Frappe handle database migrations?
Two-phase system:
1. **Automatic schema sync** — `bench migrate` reads DocType JSON files and syncs database schema
2. **Manual patches** — Python scripts in `patches.txt` for data transformations

### What is the architecture of Frappe?
Frappe follows an **MVT-like** (Model-View-Template) pattern but is more accurately described as **meta-driven MVC**:
- **Model**: DocType definitions + Python controllers
- **View**: Auto-generated forms/lists + Jinja templates
- **Controller**: Python controller classes + hooks

### How to move customizations between sites?
Use **Fixtures**:
```bash
# Export from source site
bench export-fixtures

# Install on target site
bench --site target-site install-app myapp
# or
bench --site target-site migrate
```

### Safe approach to change field type
```python
# 1. Write a patch to handle existing data
def execute():
    # Convert empty strings to 0 for float fields
    frappe.db.sql("""
        UPDATE `tabMyDocType`
        SET my_field = 0
        WHERE my_field = '' OR my_field IS NULL
    """)
    frappe.db.commit()

# 2. Then change the field type in DocType
# 3. Run bench migrate
```

---

## Best Practices

1. **Never touch the core** — always create a custom app
2. **Use hooks** for extending behavior, not monkey patching directly
3. **Use fixtures** for configuration that needs to be version-controlled
4. **Use Property Setters** for UI customizations that survive upgrades
5. **Test on staging** before applying to production
6. **Document everything** — future you will thank present you
7. **Use `ignore_permissions=True`** only in background jobs and migrations, never in user-facing code
8. **Commit after bulk operations** — `frappe.db.commit()` periodically in loops


---

## 📌 Addendum: ERPNext Customization Philosophy and Useful Tools

### The Golden Rules of Customization

1. **Never touch the core** — always create a new app to hold customizations
2. **Hooks, patches, monkey patching, custom forms, property setters, server and client scripts** are the correct ways to customize core ERPNext or any Frappe app
3. **Low-code first** — use built-in tools before writing code
4. **Test thoroughly** — customizations can impact performance, security, and upgradeability

### Customization vs Configuration vs Extension

- **Configuration**: Setting up existing features (tax rates, currencies, workflows)
- **Customization**: Modifying existing behavior (adding fields, changing logic)
- **Extension**: Adding new features that don't exist (new DocTypes, new apps)
- **Development**: Building entirely new systems from scratch

### hooks.py — The Contract with Frappe

The `hooks.py` file is like a contract between your app and the Frappe framework. It specifies exactly how and when your app participates in system events. The framework uses this configuration to dynamically compose and execute functions at runtime.

Key hooks summary:

| Hook | Purpose |
|------|---------|
| `doc_events` | Document lifecycle events (before_save, on_submit, etc.) |
| `scheduler_events` | Scheduled tasks (daily, hourly, cron) |
| `override_whitelisted_methods` | Replace built-in API methods |
| `override_doctype_class` | Replace DocType controller classes |
| `has_permission` | Custom permission logic |
| `permission_query_conditions` | Add conditions to list queries |
| `extend_bootinfo` | Modify data sent to client on login |
| `on_login` / `on_logout` | Session lifecycle hooks |
| `app_include_js` / `app_include_css` | Include custom assets |
| `doctype_js` | DocType-specific JavaScript |

### Frappe's Built-in Developer Tools

#### Permission Inspector (`/app/permission-inspector`)
Debugs why a user has or doesn't have a specific permission. Tests a combination of DocType + Document + User + Permission Type and shows detailed logs explaining the decision.

Use when: debugging permission issues, verifying configurations, troubleshooting access problems.

#### Role Permission Manager (`/app/permission-manager`)
Reviews and manages permissions for a specific role on a specific DocType. Shows all permission rules, allows adding/modifying/removing rules.

Use when: managing permissions for core/system DocTypes, bulk permission management.

#### User Permissions (`/app/user-permission`)
Restricts users to specific document records based on linked document values. Example: a Sales Manager can only see orders from their territory.

How it works:
1. Create a User Permission record
2. Select the User
3. Select the "Allow" DocType (what to restrict)
4. Select the "For Value" (specific record to allow)
5. Optionally select "Apply To" DocTypes

#### Permitted Documents For User (Report)
Shows only the documents a specific user can access. Useful for testing and verifying permission configurations.

#### Impersonate User Tool
Allows admin to log in as another user without knowing their password — for testing purposes only. Located at `/app/user/<user-name>`. Admin must provide a reason, which is notified to the user on their next login.

#### System Console (`/app/system-console`)
Run Python code or SQL queries directly from the browser. Has a "Commit" checkbox — if unchecked, changes are rolled back. Useful for testing code without creating files.

#### Commit App (Third-party)
A Frappe app that provides:
1. Lists every API in your system with documentation and testing capability
2. Draws ERD (Entity Relationship Diagram) for your database
3. Lists all bench commands as a cheat sheet

```bash
bench get-app --branch main The-commit-company/commit
bench --site {site_name} install-app commit
# Access at: http://localhost:8000/commit
```

### Customization Considerations

| Concern | Notes |
|---------|-------|
| Performance | High-code customizations can slow the system — always test |
| Maintenance | Document everything — customizations make maintenance harder |
| Security | Custom code can introduce vulnerabilities — follow best practices |
| Upgradeability | Test customizations after every Frappe/ERPNext upgrade |
| Support | Heavy customizations make community support harder |
