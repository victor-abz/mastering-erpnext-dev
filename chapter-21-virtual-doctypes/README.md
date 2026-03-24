# Chapter 21: Virtual DocTypes and Virtual Fields

## Learning Objectives

By the end of this chapter you will understand:
- What Virtual DocTypes are and when to use them
- The 7 required methods every Virtual DocType must implement
- How to build a Virtual DocType backed by an external API or file
- What Virtual Fields are and the two ways to implement them
- The difference between `@property` and the `options` expression approach

---

## 21.1 Virtual DocTypes

### What is a Virtual DocType?

A Virtual DocType is a DocType with `is_virtual = 1`. It has **no database table**. Instead, you implement 7 methods that tell Frappe how to read and write data from whatever backend you choose — an external API, a JSON file, Redis, another database, anything.

From the user's perspective it looks and behaves exactly like a regular DocType: list view, form view, permissions, workflows — all work normally.

### When to use them

- Data lives in an external system (REST API, legacy DB, file system)
- Data is read-only and always fetched fresh (system metrics, RQ workers)
- You want Frappe's UI without Frappe's database
- Temporary or in-memory data that doesn't need persistence

### Real example from Frappe core

Frappe uses a Virtual DocType to display background job workers (`RQ Worker`). The data comes from Redis Queue, not the database. The form and list view work normally — but no `tabRQ Worker` table exists.

---

## 21.2 The 7 Required Methods

Frappe validates that all 7 are implemented when you save the DocType.

### Static methods (list view)

```python
@staticmethod
def get_list(args) -> list[frappe._dict]:
    """Called for list view. Return a list of dicts."""
    ...

@staticmethod
def get_count(args) -> int:
    """Called for list view pagination. Return total count."""
    ...

@staticmethod
def get_stats(args):
    """Called for sidebar stats. Return {} if not needed."""
    ...
```

### Instance methods (CRUD)

```python
def db_insert(self, *args, **kwargs) -> None:
    """Called on doc.insert(). Save self to your backend."""
    ...

def load_from_db(self) -> None:
    """Called on frappe.get_doc(). Populate self from your backend."""
    ...

def db_update(self, *args, **kwargs) -> None:
    """Called on doc.save(). Update your backend."""
    ...

def delete(self, *args, **kwargs) -> None:
    """Called on doc.delete(). Remove from your backend."""
    ...
```

---

## 21.3 Step-by-Step: JSON File Backend

This is the canonical example from Frappe's own test suite.

### Step 1: Create the DocType

1. Go to **DocType List → New**
2. Add your fields
3. Check **Is Virtual**
4. Save

### Step 2: Create the controller

```python
# my_app/my_app/doctype/product_catalog/product_catalog.py

import json
import os
import frappe
from frappe.model.document import Document

DATA_FILE = "/tmp/product_catalog.json"

def _read() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE) as f:
        return json.load(f)

def _write(data: dict) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


class ProductCatalog(Document):

    # ── Static methods (list view) ──────────────────────────────────────

    @staticmethod
    def get_list(args):
        data = _read()
        start = int(args.get("start") or 0)
        page_length = int(args.get("page_length") or 20)
        items = list(data.values())
        return [frappe._dict(item) for item in items[start : start + page_length]]

    @staticmethod
    def get_count(args):
        return len(_read())

    @staticmethod
    def get_stats(args):
        return {}

    # ── Instance methods (CRUD) ─────────────────────────────────────────

    def db_insert(self, *args, **kwargs):
        data = _read()
        data[self.name] = self.get_valid_dict(convert_dates_to_str=True)
        _write(data)

    def load_from_db(self):
        data = _read()
        record = data.get(self.name)
        if not record:
            raise frappe.DoesNotExistError(f"ProductCatalog {self.name} not found")
        super(Document, self).__init__(record)

    def db_update(self, *args, **kwargs):
        # For this backend, insert and update are the same operation
        self.db_insert()

    def delete(self, *args, **kwargs):
        data = _read()
        data.pop(self.name, None)
        _write(data)
```

### Step 3: Use it

```python
# Create
doc = frappe.new_doc("Product Catalog")
doc.product_name = "Widget Pro"
doc.price = 99.99
doc.insert()

# Read
doc = frappe.get_doc("Product Catalog", "widget-pro")
print(doc.price)

# Update
doc.price = 89.99
doc.save()

# List
products = frappe.get_list("Product Catalog", fields=["name", "product_name", "price"])

# Delete
doc.delete()
```

---

## 21.4 External API Backend

```python
# my_app/my_app/doctype/weather_reading/weather_reading.py

import frappe
import requests
from frappe.model.document import Document

API_BASE = "https://api.example.com/weather"

class WeatherReading(Document):

    @staticmethod
    def get_list(args):
        resp = requests.get(f"{API_BASE}/readings", params={
            "start": args.get("start", 0),
            "limit": args.get("page_length", 20),
        })
        resp.raise_for_status()
        return [frappe._dict(r) for r in resp.json()["data"]]

    @staticmethod
    def get_count(args):
        resp = requests.get(f"{API_BASE}/readings/count")
        return resp.json()["count"]

    @staticmethod
    def get_stats(args):
        return {}

    def load_from_db(self):
        resp = requests.get(f"{API_BASE}/readings/{self.name}")
        if resp.status_code == 404:
            raise frappe.DoesNotExistError
        super(Document, self).__init__(resp.json())

    def db_insert(self, *args, **kwargs):
        requests.post(f"{API_BASE}/readings", json=self.as_dict())

    def db_update(self, *args, **kwargs):
        requests.put(f"{API_BASE}/readings/{self.name}", json=self.as_dict())

    def delete(self, *args, **kwargs):
        requests.delete(f"{API_BASE}/readings/{self.name}")
```

---

## 21.5 Read-Only Virtual DocType (e.g. system metrics)

When data is managed externally and Frappe should never write to it, implement the write methods as no-ops:

```python
class SystemMetric(Document):

    @staticmethod
    def get_list(args):
        return get_current_metrics()  # from /proc, psutil, etc.

    @staticmethod
    def get_count(args):
        return len(get_current_metrics())

    @staticmethod
    def get_stats(args):
        return {}

    def load_from_db(self):
        metrics = {m["name"]: m for m in get_current_metrics()}
        record = metrics.get(self.name)
        if not record:
            raise frappe.DoesNotExistError
        super(Document, self).__init__(record)

    # Read-only — these are intentional no-ops
    def db_insert(self, *args, **kwargs): pass
    def db_update(self, *args, **kwargs): pass
    def delete(self, *args, **kwargs): pass
```

---

## 21.6 Virtual Fields

A Virtual Field is a field within a regular DocType that has **no database column**. Its value is computed on the fly.

Set `is_virtual = 1` on the field in the DocType editor.

### Method 1: `@property` decorator (recommended for complex logic)

```python
# sales_order.py
from frappe.model.document import Document

class SalesOrder(Document):

    @property
    def total_weight(self):
        """Sum of item weights — computed, not stored."""
        return sum(
            (item.qty or 0) * (item.weight_per_unit or 0)
            for item in self.items
        )

    @property
    def is_overdue(self):
        """True if delivery date has passed and order is not delivered."""
        from frappe.utils import getdate, nowdate
        if self.delivery_date and self.status != "Delivered":
            return getdate(self.delivery_date) < getdate(nowdate())
        return False

    @property
    def customer_email(self):
        """Fetched from Customer — no join needed in queries."""
        if self.customer:
            return frappe.db.get_value("Customer", self.customer, "email_id")
        return None
```

Access in code (no parentheses — it's a property):

```python
order = frappe.get_doc("Sales Order", "SO-0001")
print(order.total_weight)   # computed
print(order.is_overdue)     # computed
print(order.customer_email) # fetched
```

### Method 2: `options` expression (for simple one-liners)

In the DocType field definition, set the **Options** field to a Python expression. The variable `doc` is available.

```python
# Full name from two fields
doc.first_name + " " + doc.last_name

# Age from date of birth
frappe.utils.date_diff(frappe.utils.nowdate(), doc.date_of_birth) // 365

# Sum of child table
sum(item.amount for item in doc.items)

# Boolean flag
doc.status == "Active"
```

Frappe evaluates this with `frappe.safe_eval()` — a sandboxed Python evaluator.

---

## 21.7 Virtual Fields in Forms

Virtual fields appear in forms but are **read-only** — you cannot `frm.set_value()` on them.

```javascript
frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        // Virtual field value is available
        console.log("Total weight:", frm.doc.total_weight);
        console.log("Is overdue:", frm.doc.is_overdue);

        // Highlight overdue orders
        if (frm.doc.is_overdue) {
            frm.dashboard.set_headline_alert(
                __("This order is overdue"),
                "red"
            );
        }
    },
});
```

---

## 21.8 Adding Virtual Fields via Custom Field

You can add virtual fields to **any DocType** — including ERPNext core DocTypes — without modifying the DocType definition:

```python
# In after_install or a patch
custom_field = frappe.get_doc({
    "doctype": "Custom Field",
    "dt": "Sales Order",
    "fieldname": "total_weight_virtual",
    "label": "Total Weight",
    "fieldtype": "Float",
    "is_virtual": 1,
    "insert_after": "items",
    "options": "sum((item.qty or 0) * (item.weight_per_unit or 0) for item in doc.items)",
})
custom_field.insert()
```

---

## 21.9 Comparison

### Virtual DocType vs Regular DocType

| | Regular DocType | Virtual DocType |
|--|----------------|-----------------|
| Database table | Yes | No |
| Data storage | MariaDB | Your backend |
| CRUD | Automatic | You implement 7 methods |
| List view | Yes | Yes (via `get_list`) |
| Permissions | Yes | Yes |
| Workflows | Yes | Yes |
| Search/filter | Yes | Custom |

### `@property` vs `options` expression

| | `@property` | `options` expression |
|--|------------|---------------------|
| Complexity | Any Python | Simple one-liners |
| Debugging | Easy | Harder |
| Caching | Use `@cached_property` | No caching |
| Best for | Complex logic | Quick computed values |

---

## Summary

Virtual DocTypes let you use Frappe's full UI — forms, list views, permissions, workflows — for data that lives anywhere. You implement 7 methods and Frappe handles the rest.

Virtual Fields let you add computed, derived, or fetched values to any DocType without adding a database column. Use `@property` for logic, use `options` for simple expressions.

Both features are increasingly important in v15/v16 as Frappe apps integrate more with external systems.

---

**Next Chapter**: AI Integration — adding intelligent features to ERPNext applications.
