# Chapter 22: Patches and Migrations

## What is a Patch in Frappe?

A patch is a tiny Python script that:
1. Runs automatically during migrations (`bench migrate`)
2. Fixes or updates database schema or data
3. Gets recorded so it **only runs once** — even if you run `bench migrate` 1000 times

Frappe opens it once, reads it, runs the `execute()` function, and logs it as "done."

---

## When to Write a Patch

Patches are used when you make a change in existing functionality and want to update instances already running ERPNext. They are **never run twice** and **never run on a new site**.

**Classic example**: Renaming the "School" module to "Education". On a new site, the DocType is already named "Education". On an older site, you need a patch to rename it.

### Real-life use cases:
- Add a unique constraint to two fields in a DocType
- Update old customer names to match new rules
- Remove test data from a live site
- Migrate values from an old field to a new one
- Add a missing column or update field types

---

## How to Write a Patch

### Step 1: Create the patch file

```python
# File: your_app/patches/v1_0/add_unique_booking_constraint.py
import frappe

def execute():
    frappe.db.add_unique("Booking", ["customer", "booking_date"])
```

**Rules:**
- The function **must** be named `execute` — this is how `bench migrate` detects it
- Use versioned folder names like `v1_0/` for clarity and maintenance

### Step 2: Register in `patches.txt`

```text
your_app.patches.v1_0.add_unique_booking_constraint
```

### Step 3: Run migration

```bash
bench --site yoursite migrate
```

This checks which patches haven't been applied yet (based on the **Patch Log**) and executes them safely.

---

## How Frappe Prevents Re-Running Patches

Once a patch runs, Frappe logs it in the **Patch Log** DocType. Even if you run `bench migrate` a hundred times, it won't run again — unless you manually delete the entry from Patch Log.

---

## More Patch Examples

### Data migration patch

```python
# your_app/patches/v2_0/migrate_customer_names.py
import frappe

def execute():
    # Rename all customers with old prefix
    frappe.db.sql("""
        UPDATE `tabCustomer`
        SET customer_name = CONCAT('NEW_', customer_name)
        WHERE customer_name NOT LIKE 'NEW_%'
    """)
    frappe.db.commit()
```

### Field value migration

```python
# your_app/patches/v2_1/move_field_values.py
import frappe

def execute():
    # Move data from old_field to new_field
    frappe.db.sql("""
        UPDATE `tabSales Invoice`
        SET new_field = old_field
        WHERE new_field IS NULL AND old_field IS NOT NULL
    """)
    frappe.db.commit()
```

### Schema change patch

```python
# your_app/patches/v3_0/add_index_to_sales_invoice.py
import frappe

def execute():
    if not frappe.db.has_index("Sales Invoice", "customer_posting_date"):
        frappe.db.add_index("Sales Invoice", ["customer", "posting_date"])
```

### Conditional patch (safe to re-run)

```python
# your_app/patches/v3_1/set_default_status.py
import frappe

def execute():
    frappe.db.sql("""
        UPDATE `tabAsset`
        SET status = 'Active'
        WHERE status IS NULL OR status = ''
    """)
    frappe.db.commit()
```

---

## Patch File Organization

```
your_app/
├── patches/
│   ├── __init__.py
│   ├── v1_0/
│   │   ├── __init__.py
│   │   └── add_unique_booking_constraint.py
│   ├── v2_0/
│   │   ├── __init__.py
│   │   └── migrate_customer_names.py
│   └── v3_0/
│       ├── __init__.py
│       └── add_index_to_sales_invoice.py
└── patches.txt
```

### patches.txt ordering matters

```text
# patches.txt — order is important, top runs first
your_app.patches.v1_0.add_unique_booking_constraint
your_app.patches.v2_0.migrate_customer_names
your_app.patches.v3_0.add_index_to_sales_invoice
```

---

## Best Practices

1. **Always test on staging** before running on production
2. **Always backup** your database before production migrations
3. **Keep patches well-named** — `v1_0/fix_duplicate_emails.py` is better than `patch1.py`
4. **If a patch fails**, fix it and re-run after clearing it from the Patch Log
5. **Use `frappe.db.commit()`** after DML operations (UPDATE/INSERT/DELETE)
6. **Make patches idempotent** when possible — safe to run even if somehow triggered twice

---

## Interview Q&A

**Q: What is a patch in Frappe?**
A: A Python script used to apply database changes, fix issues, or modify data after an update. Defined in `patches.txt`, each patch runs exactly once per site.

**Q: When would you use a patch script?**
A: Adding new fields to existing DocTypes, migrating data from one format to another, fixing data inconsistencies, or applying schema changes to live sites.

**Q: How do you handle data migrations when upgrading ERPNext?**
A: Write patch scripts, always take a database backup first, test in staging, and review release notes for breaking changes.

**Q: How does Frappe know not to re-run a patch?**
A: It logs the patch module path in the **Patch Log** DocType. On subsequent `bench migrate` runs, already-logged patches are skipped.


---

## 📌 Addendum: Patches Deep Dive — Theory, Philosophy, and Data Migration

### What "Patch" Means in Software

In software terms, a patch is a group of things executed sequentially, once, and never run again. Frappe patches are Python scripts that:
1. Run automatically during `bench migrate`
2. Fix or update database schema or data
3. Get recorded in `tabPatch Log` so they **only run once** — even across 1000 `bench migrate` calls

### The Classic Example

Renaming the "School" module to "Education":
- On a **new site**: the DocType is already named "Education" — no patch needed
- On an **older site**: the DocType was named "School" — a patch renames it to "Education"

This is the core use case: patches bridge the gap between old running instances and new code.

### When Patches Run vs When They Don't

Patches are **never run on a new site** and **never run twice on the same site** (unless you manually delete the Patch Log entry).

### `[pre_model_sync]` vs `[post_model_sync]`

```text
# patches.txt
[pre_model_sync]
# Runs BEFORE DocType schema sync
# Use for: renaming DocTypes, preparing data before schema changes
myapp.patches.v2_0.rename_old_doctype

[post_model_sync]
# Runs AFTER DocType schema sync
# Use for: migrating data into new fields, fixing data after schema changes
myapp.patches.v2_0.migrate_data_to_new_field
execute:frappe.reload_doc('stock', 'doctype', 'item')
```

The `execute:` prefix lets you run one-liner Frappe commands directly in `patches.txt`.

### Data Migration from External Systems

When migrating data from an external system into ERPNext:

**1. Preparation**
- Map external fields to ERPNext DocTypes
- Identify dependencies (Customers before Sales Orders)
- Determine migration order: master data → transactions

**2. Migration Methods**

**Data Import Tool (UI)** — best for CSV files, non-technical users, < 10,000 records:
- Navigate to DocType → Menu → Import
- Download template, fill data, upload

**ORM Scripts** (recommended for developers):
```python
import frappe
import csv

def migrate_customers():
    with open('customers.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not frappe.db.exists("Customer", row['customer_id']):
                doc = frappe.get_doc({
                    "doctype": "Customer",
                    "customer_name": row['name'],
                    "customer_type": row['type'],
                    "territory": row['region']
                })
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
```

**Background Jobs** (for large datasets):
```python
def enqueue_migration():
    total_records = get_total_count()
    chunk_size = 1000
    
    for offset in range(0, total_records, chunk_size):
        frappe.enqueue(
            "myapp.migration.migrate_chunk",
            queue="long",
            timeout=3600,
            offset=offset,
            limit=chunk_size
        )
```

**3. Error Handling Pattern**
```python
def safe_migrate():
    failed_records = []
    success_count = 0
    
    for record in source_data:
        try:
            create_document(record)
            success_count += 1
        except Exception as e:
            failed_records.append({"record": record, "error": str(e)})
            frappe.log_error(
                title=f"Migration failed for {record.get('id')}",
                message=frappe.get_traceback()
            )
    
    print(f"Success: {success_count}, Failed: {len(failed_records)}")
```

### Migration Flow (Full Picture)

```
bench migrate
├── Run before_migrate hooks
├── Run [pre_model_sync] patches
├── Sync all DocTypes (automatic schema changes)
│   ├── Adds new columns
│   ├── Modifies column types
│   ├── Adds/drops indexes
│   └── Does NOT drop columns (safety)
├── Run [post_model_sync] patches
└── Run after_migrate hooks
```

### Changing Field Types Safely

A common pitfall: changing a field type to Float when existing records contain empty strings or NULL.

```python
# Patch: prepare data BEFORE changing field type
def execute():
    """Convert empty strings to 0 before changing field to Float"""
    frappe.db.sql("""
        UPDATE `tabMyDocType`
        SET my_field = 0
        WHERE my_field = '' OR my_field IS NULL
    """)
    frappe.db.commit()
```

Then change the field type in the DocType, then run `bench migrate`.

Why this matters: Frappe performs type casting at the ORM level when loading DocTypes. If existing data contains `""` and the field is now `Float`, Python's `float("")` raises `ValueError`.

### Interview Q&A

**Q: Why does Frappe not rely only on database data types for type casting?**
A: Frappe enforces its own type casting at the ORM level for cross-database compatibility (MySQL, MariaDB, PostgreSQL), consistent behavior regardless of DB engine, and to handle edge cases like empty strings that databases allow but Python types don't.

**Q: What is the correct approach to safely change a field type?**
A: Write a `[pre_model_sync]` patch to clean/convert existing data, then change the field type in the DocType JSON, then run `bench migrate`.

**Q: If the company changes all employee emails, how to update them safely?**
A: Write a patch using `frappe.db.sql()` with proper WHERE conditions, test on staging, backup production, then run. Never do bulk updates directly in production without a patch.
