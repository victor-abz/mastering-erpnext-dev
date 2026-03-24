# Chapter 18: Hooks Deep Dive — The Extension Architecture

## Learning Objectives

By the end of this chapter you will understand:
- The philosophy and theory behind Frappe's hook system
- How Frappe discovers, loads, and caches hooks at runtime
- Every built-in hook type and when to use each one
- How to create custom hook types for your own apps
- Advanced patterns: conditional hooks, error handling, composition

---

## 18.1 What Are Hooks?

Think of hooks as **pre-wired connection points** in the framework. Instead of modifying Frappe's core code to add behaviour, you declare what you want to happen and Frappe calls your code at the right moment.

This is the **inversion of control** principle: the framework drives execution, your app registers interest.

```python
# Without hooks — you'd have to edit Frappe's core Customer code
# With hooks — you declare intent in your own app
doc_events = {
    "Customer": {
        "after_insert": "my_app.events.send_welcome_email"
    }
}
```

When a Customer is created, Frappe finds your function and calls it automatically. No core modification needed.

### Key benefits

- Your code won't break Frappe's core functionality
- Multiple apps can hook the same event without conflict
- Easy to enable/disable by commenting out the registration
- Frappe caches all hooks for performance

---

## 18.2 How Frappe Discovers Hooks

When Frappe initialises, it runs `_load_app_hooks()` which iterates every installed app and imports its `hooks.py`:

```python
# Simplified from frappe/__init__.py
def _load_app_hooks(app_name=None):
    hooks = {}
    apps = [app_name] if app_name else get_installed_apps()

    for app in apps:
        try:
            app_hooks = get_module(f"{app}.hooks")
        except ImportError:
            continue  # App has no hooks.py — skip silently

        def _is_valid_hook(obj):
            # Exclude modules, functions, and classes — only data
            return not isinstance(obj, (types.ModuleType, types.FunctionType, type))

        for key, value in inspect.getmembers(app_hooks, predicate=_is_valid_hook):
            if not key.startswith("_"):
                append_hook(hooks, key, value)

    return hooks
```

**Key insight**: Frappe loads **any non-private variable** from `hooks.py`. There is no hardcoded list of valid hook names. This means you can create your own hook types too (see §18.6).

The merged hooks are cached per request. Clear with `bench clear-cache` or `frappe.clear_cache()`.

---

## 18.3 Document Event Hooks

The most commonly used hook type. Fires at specific points in the document lifecycle.

```python
# hooks.py
doc_events = {
    "Sales Order": {
        "before_insert":  "my_app.events.so_before_insert",
        "after_insert":   "my_app.events.so_after_insert",
        "validate":       "my_app.events.so_validate",
        "on_update":      "my_app.events.so_on_update",
        "before_submit":  "my_app.events.so_before_submit",
        "on_submit":      "my_app.events.so_on_submit",
        "before_cancel":  "my_app.events.so_before_cancel",
        "on_cancel":      "my_app.events.so_on_cancel",
        "on_trash":       "my_app.events.so_on_trash",
        "after_delete":   "my_app.events.so_after_delete",
    },
    # Apply to ALL doctypes
    "*": {
        "after_insert": "my_app.events.log_all_creates"
    }
}
```

### Document lifecycle order

```
insert()
  → before_insert
  → validate
  → db_insert          ← actual DB write
  → after_insert
  → on_update

save()
  → before_save
  → validate
  → db_update          ← actual DB write
  → on_update

submit()
  → before_submit
  → db_update (docstatus=1)
  → on_submit
  → on_update

cancel()
  → before_cancel
  → db_update (docstatus=2)
  → on_cancel
  → on_update

delete()
  → on_trash           ← DB record still exists
  → [deletion happens]
  → after_delete       ← DB record gone
```

### Hook function signature

```python
# events.py
import frappe

def so_on_submit(doc, method):
    """
    doc    — the Document instance
    method — the event name string, e.g. "on_submit"
    """
    try:
        notify_warehouse_team(doc)
        create_delivery_schedule(doc)
    except Exception:
        # Log but don't block submission
        frappe.log_error(frappe.get_traceback(), f"so_on_submit failed for {doc.name}")
```

### Useful flags inside hooks

```python
def validate(doc, method):
    # Skip expensive checks during bulk data import
    if frappe.flags.in_import:
        return

    # Skip during test runs if needed
    if frappe.flags.in_test:
        return

    # Skip during bench migrate patches
    if frappe.flags.in_patch:
        return

    run_expensive_validation(doc)
```

| Flag | Set by |
|------|--------|
| `frappe.flags.in_import` | Data Import tool |
| `frappe.flags.in_test` | Test runner |
| `frappe.flags.in_patch` | `bench migrate` |
| `frappe.flags.in_install` | App installation |
| `frappe.flags.ignore_permissions` | Tests / migrations |

---

## 18.4 Scheduler Event Hooks

Run Python functions on a time-based schedule via Frappe's background job system.

```python
# hooks.py
scheduler_events = {
    "all":     ["my_app.tasks.run_every_few_minutes"],
    "hourly":  ["my_app.tasks.sync_external_data"],
    "daily":   ["my_app.tasks.send_expiry_notifications",
                "my_app.tasks.cleanup_old_logs"],
    "weekly":  ["my_app.tasks.generate_weekly_report"],
    "monthly": ["my_app.tasks.archive_old_records"],
    # Cron syntax for precise timing
    "cron": {
        "0 2 * * *": ["my_app.tasks.midnight_processing"],   # 2 AM daily
        "*/15 * * * *": ["my_app.tasks.every_15_minutes"],   # every 15 min
    }
}
```

### Example scheduled task

```python
# tasks.py
import frappe
from frappe.utils import nowdate, add_to_date

def send_expiry_notifications():
    """Daily: notify users of documents expiring in 30 days."""
    try:
        expiring = frappe.get_all(
            "Contract",
            filters={
                "end_date": ["between", [nowdate(), add_to_date(nowdate(), days=30)]],
                "status": "Active",
            },
            fields=["name", "customer", "end_date"],
        )

        for contract in expiring:
            frappe.sendmail(
                recipients=[frappe.db.get_value("Customer", contract.customer, "email_id")],
                subject=f"Contract {contract.name} expiring soon",
                message=f"Your contract expires on {contract.end_date}.",
            )

        frappe.logger().info(f"Sent {len(expiring)} expiry notifications")

    except Exception:
        frappe.log_error(frappe.get_traceback(), "send_expiry_notifications failed")
```

---

## 18.5 Request Lifecycle Hooks

> **Correction:** `before_request` and `after_request` are **not** listed in the official Frappe hooks reference. For request-level authentication, use `auth_hooks`. For session lifecycle events, use `on_login`, `on_session_creation`, and `on_logout`.

```python
# hooks.py — correct hooks for request/session lifecycle
auth_hooks = ["my_app.middleware.validate_token"]
on_login = "my_app.middleware.on_login"
on_session_creation = "my_app.middleware.on_session_creation"
on_logout = "my_app.middleware.on_logout"
```

```python
# middleware.py
import frappe

def validate_token():
    """Runs during request authentication. Validate custom headers here."""
    pass

def on_session_creation(login_manager):
    frappe.logger().debug(f"Session created for {frappe.session.user}")
```

---

## 18.6 Permission Hooks

Extend Frappe's permission system with custom logic.

```python
# hooks.py
has_permission = {
    "Asset": "my_app.permissions.has_asset_permission"
}

permission_query_conditions = {
    "Asset": "my_app.permissions.get_asset_conditions"
}
```

```python
# permissions.py
import frappe

def has_asset_permission(doc, user=None):
    """Return True/False for document-level access."""
    user = user or frappe.session.user
    if "Asset Manager" in frappe.get_roles(user):
        return True
    # Employees can only see assets assigned to them
    return frappe.db.exists("Asset Assignment", {"asset": doc.name, "assigned_to": user, "docstatus": 1})

def get_asset_conditions(user):
    """Return a SQL WHERE clause fragment for list queries."""
    if "Asset Manager" in frappe.get_roles(user):
        return ""  # No restriction
    assigned = frappe.get_all("Asset Assignment",
        filters={"assigned_to": user, "docstatus": 1}, pluck="asset")
    if not assigned:
        return "1=0"
    names = "', '".join(assigned)
    return f"`tabAsset`.name IN ('{names}')"
```

---

## 18.7 UI and Asset Hooks

Include custom JavaScript and CSS in the Frappe desk.

```python
# hooks.py

# Included on every desk page
app_include_js  = ["my_app.bundle.js"]
app_include_css = ["my_app.bundle.css"]

# Included only on specific DocType forms
doctype_js  = {"Sales Order": "public/js/sales_order.js"}
doctype_css = {"Sales Order": "public/css/sales_order.css"}

# Included on website pages (not desk)
web_include_js  = ["my_app/public/js/website.js"]
web_include_css = ["my_app/public/css/website.css"]
```

---

## 18.8 Override Hooks

Replace Frappe's default classes and API methods.

```python
# hooks.py

# Replace the Document class for a specific DocType
override_doctype_class = {
    "Customer": "my_app.overrides.CustomCustomer"
}

# Replace a whitelisted API method
override_whitelisted_methods = {
    "frappe.desk.query_report.get_report_data": "my_app.overrides.custom_report_data"
}
```

```python
# overrides.py
import frappe
from erpnext.selling.doctype.customer.customer import Customer

class CustomCustomer(Customer):
    def validate(self):
        super().validate()
        self.custom_validation()

    def custom_validation(self):
        if not self.custom_field:
            frappe.throw("Custom field is required")
```

---

## 18.9 Application Lifecycle Hooks

Run code during app installation and migration.

```python
# hooks.py
before_install = "my_app.setup.before_install"
after_install  = "my_app.setup.after_install"
before_migrate = "my_app.setup.before_migrate"
after_migrate  = "my_app.setup.after_migrate"
```

```python
# setup.py
import frappe

def after_install():
    """Create initial roles and data after app install."""
    create_roles()
    create_default_settings()
    frappe.db.commit()

def create_roles():
    for role_name in ["My App Manager", "My App User"]:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert()
```

---

## 18.10 Custom Hook Types

Because Frappe loads **any variable** from `hooks.py`, you can invent your own hook types and call them from your own code.

```python
# hooks.py — define a custom hook type
my_data_processors = [
    "my_app.processors.validate_customer_data",
    "my_app.processors.enrich_customer_data",
]
```

```python
# In your business logic — call the custom hooks
import frappe

def process_customer(doc):
    for fn_path in frappe.get_hooks("my_data_processors"):
        frappe.get_attr(fn_path)(doc)
```

This is exactly how Frappe itself uses hooks like `extend_bootinfo` and `get_changelog_feed` — they are just variables in `frappe/hooks.py` that Frappe reads with `frappe.get_hooks()`.

### Real example from Frappe core

```python
# frappe/hooks.py
extend_bootinfo = [
    "frappe.utils.telemetry.add_bootinfo",
    "frappe.core.doctype.user_permission.user_permission.send_user_permissions",
]

# frappe/sessions.py — calling the custom hook
for hook in frappe.get_hooks("extend_bootinfo"):
    frappe.get_attr(hook)(bootinfo=bootinfo)
```

---

## 18.11 Hook Execution Patterns

### Multiple apps, same event

When multiple apps register the same event, all functions run in app installation order:

```python
# app1/hooks.py
doc_events = {"Customer": {"after_insert": "app1.events.send_email"}}

# app2/hooks.py
doc_events = {"Customer": {"after_insert": "app2.events.create_task"}}

# Both run — app1's function first, then app2's
```

### Error isolation

```python
def robust_hook(doc, method):
    try:
        do_something(doc)
    except Exception:
        # Log but don't block the main document operation
        frappe.log_error(frappe.get_traceback(), f"robust_hook failed: {doc.name}")
```

### Conditional execution

```python
def conditional_hook(doc, method):
    # Only run for specific conditions
    if doc.customer_type != "Company":
        return
    if frappe.flags.in_import:
        return
    process_company_customer(doc)
```

---

## Summary

Frappe's hook system is built on a single principle: **declare intent, let the framework execute**. Every variable in `hooks.py` is a potential hook. The framework discovers them at startup, merges them across all installed apps, caches the result, and calls your functions at the right moment.

The most important hook types:

| Hook | Purpose |
|------|---------|
| `doc_events` | React to document lifecycle events |
| `scheduler_events` | Time-based background tasks |
| `auth_hooks` | HTTP request authentication |
| `has_permission` / `permission_query_conditions` | Custom access control |
| `app_include_js` / `doctype_js` | Custom UI assets |
| `override_doctype_class` | Replace document classes |
| `after_install` / `after_migrate` | App setup and migration |
| *(any name)* | Your own custom hook types |

---

**Next Chapter**: Workflows — managing document approval processes with states and transitions.


---

## 📌 Addendum: Hooks — Complete Theory, Philosophy, and Custom Hook Types

### The Philosophy Behind Hooks

Hooks represent one of the most elegant architectural patterns in modern software development. They allow applications to extend functionality without modifying the core codebase.

**Key philosophical principles:**
1. **Inversion of Control** — the framework controls execution flow; applications register their interest
2. **Declarative over Imperative** — declare what you want to do, not how to do it
3. **Composition over Inheritance** — compose functionality through simple function definitions
4. **Open-Closed Principle** — open for extension, closed for modification

### Hooks in the Software Industry

Hooks have a rich history:
- **C/Assembly era**: function pointers and callbacks for interrupts
- **OOP era**: Observer pattern — objects subscribe to events
- **Plugin era**: entire modules dynamically loaded (browser extensions, VS Code plugins)
- **Modern era**: React hooks, Angular lifecycle hooks, Frappe hooks

### How Frappe Discovers Hooks

When Frappe starts, `_load_app_hooks()` iterates through all installed apps and loads their `hooks.py` files:

```python
def _load_app_hooks(app_name=None):
    hooks = {}
    apps = [app_name] if app_name else get_installed_apps()
    
    for app in apps:
        try:
            app_hooks = get_module(f"{app}.hooks")
        except ImportError:
            pass
        
        def _is_valid_hook(obj):
            return not isinstance(obj, types.ModuleType | types.FunctionType | type)
        
        for key, value in inspect.getmembers(app_hooks, predicate=_is_valid_hook):
            if not key.startswith("_"):
                append_hook(hooks, key, value)
    return hooks
```

**Key insight**: Frappe loads **ANY** non-private attribute from your `hooks.py` as a potential hook. There is no predefined list of valid hook types.

### All Hook Types Reference

#### Application Lifecycle Hooks

```python
before_install = "my_app.hooks.check_requirements"
after_install = "my_app.hooks.setup_initial_data"
before_migrate = "my_app.hooks.backup_data"
after_migrate = "my_app.hooks.update_database"
```

#### Document Event Hooks

```python
doc_events = {
    "Customer": {
        "before_insert": "my_app.hooks.validate_customer",
        "after_insert": "my_app.hooks.send_welcome_email",
        "before_save": "my_app.hooks.calculate_totals",
        "on_update": "my_app.hooks.update_related_docs",
        "before_submit": "my_app.hooks.pre_submit_check",
        "on_submit": "my_app.hooks.create_invoice",
        "before_cancel": "my_app.hooks.pre_cancel_check",
        "on_cancel": "my_app.hooks.reverse_transactions",
        "on_trash": "my_app.hooks.cleanup_data",
        "before_update_after_submit": "my_app.hooks.validate_amendment",
        "on_update_after_submit": "my_app.hooks.post_amendment_update",
    },
    "*": {  # Apply to ALL doctypes
        "after_insert": "my_app.hooks.log_all_creates"
    }
}
```

#### Scheduler Event Hooks

```python
scheduler_events = {
    "all": ["my_app.hooks.run_every_minute"],
    "hourly": ["my_app.hooks.sync_data"],
    "daily": ["my_app.hooks.cleanup_old_files"],
    "weekly": ["my_app.hooks.generate_reports"],
    "monthly": ["my_app.hooks.archive_data"],
    "cron": {
        "0 2 * * *": ["my_app.hooks.midnight_processing"]  # 2 AM daily
    }
}
```

#### Request / Session Lifecycle Hooks

```python
# Note: before_request / after_request are not valid Frappe hooks.
# Use auth_hooks for request authentication, on_login/on_session_creation for session events.
auth_hooks = ["my_app.hooks.validate_token"]
on_login = "my_app.hooks.on_login"
on_session_creation = "my_app.hooks.on_session_creation"
on_logout = "my_app.hooks.on_logout"
```

#### Permission Hooks

```python
has_permission = {
    "Customer": "my_app.hooks.check_customer_access"
}

permission_query_conditions = {
    "Customer": "my_app.hooks.add_customer_filters"
}

# Implementation
def check_customer_access(doc, user):
    if doc.owner == user:
        return True
    return False

def add_customer_filters(user):
    return f"`tabCustomer`.owner = '{user}'"
```

#### UI and Asset Hooks

```python
app_include_js = ["my_app.bundle.js"]
app_include_css = ["my_app.bundle.css"]

doctype_js = {
    "Customer": "public/js/customer.js"
}

doctype_css = {
    "Customer": "public/css/customer.css"
}

web_include_js = ["my_app/public/js/website.js"]
web_include_css = ["my_app/public/css/website.css"]
```

#### Override Hooks

```python
override_doctype_class = {
    "Customer": "my_app.overrides.CustomCustomer"
}

override_whitelisted_methods = {
    "frappe.desk.query_report.get_report_data": "my_app.overrides.custom_report_data"
}
```

### Hook vs Hook Type: The Key Difference

**Hook Type** is the **category/name** (like `doc_events`, `scheduler_events`) — it's the trigger/when.

**Hook** is the **actual function** that gets executed — it's the action/what.

```python
# "doc_events" = HOOK TYPE (the trigger)
doc_events = {
    "Customer": {
        "after_insert": "my_app.hooks.send_email"  # "send_email" = HOOK (the action)
    }
}
```

### Creating Custom Hook Types

Since Frappe loads ANY non-private attribute from `hooks.py`, you can create your own hook types:

```python
# In your_app/hooks.py

# Simple list-based custom hook
custom_logging_hooks = [
    "your_app.hooks.log_user_action",
    "your_app.hooks.log_system_event"
]

# Dictionary-based custom hook
data_validation_hooks = {
    "Customer": "your_app.hooks.validate_customer_data",
    "Item": "your_app.hooks.validate_item_data",
}

# Accessing your custom hooks anywhere
custom_hooks = frappe.get_hooks("custom_logging_hooks")
for hook_func in custom_hooks:
    frappe.get_attr(hook_func)()
```

### Real Examples from Frappe Codebase

```python
# extend_bootinfo — allows apps to extend boot information
extend_bootinfo = [
    "frappe.utils.telemetry.add_bootinfo",
    "frappe.core.doctype.user_permission.user_permission.send_user_permissions",
]

# Used in frappe/sessions.py:
for hook in frappe.get_hooks("extend_bootinfo"):
    frappe.get_attr(hook)(bootinfo=bootinfo)

# standard_navbar_items — customize navbar
standard_navbar_items = [
    {
        "item_label": "My Profile",
        "item_type": "Route",
        "route": "/app/user-profile",
        "is_standard": 1,
    },
]
```

### Hook Execution Flow

1. **User creates a Customer document**
2. **Frappe checks**: "What hooks are registered for Customer + after_insert?"
3. **Frappe finds**: `["my_app.hooks.send_email"]`
4. **Frappe calls**: `frappe.get_attr("my_app.hooks.send_email")(doc, "after_insert")`
5. **Your function runs**
6. **Frappe continues** with the normal process

Multiple apps can register hooks for the same event — Frappe runs all of them in order.

### Advanced Hook Patterns

```python
# Conditional hook execution
def conditional_hook(doc, method):
    if doc.doctype == "Customer" and doc.customer_type == "Company":
        # Your logic here
        pass

# Hook with error handling (don't break the main process)
def robust_hook(doc, method):
    try:
        # Your hook logic here
        pass
    except Exception as e:
        frappe.logger().error(f"Hook error: {str(e)}")
        # Don't re-raise unless critical

# Hook with database transactions
def transactional_hook(doc, method):
    try:
        frappe.db.sql("UPDATE `tabYour Table` SET field = %s WHERE name = %s",
                     [value, doc.name])
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise

# Hook with logging
def logged_hook(doc, method):
    frappe.logger().info(f"Executing hook for {doc.doctype} - {method}")
    try:
        # Your logic
        frappe.logger().info("Hook executed successfully")
    except Exception as e:
        frappe.logger().error(f"Hook execution failed: {str(e)}")
        raise
```

### Caching and Performance

Hooks are cached in memory after first load:
```python
# Clear hook cache if hooks aren't updating
frappe.cache.delete_value("app_hooks")
# Or clear all cache
frappe.clear_cache()
```

### Testing Hooks

```python
# Enable developer mode to see detailed errors
# In site_config.json: {"developer_mode": 1}

# Test by triggering the event and checking logs
# Or write unit tests:
def test_welcome_email_hook():
    customer = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": "Test Corp"
    })
    customer.insert()
    # Assert email was sent
    emails = frappe.get_all("Email Queue", filters={"reference_name": customer.name})
    assert len(emails) > 0
```
