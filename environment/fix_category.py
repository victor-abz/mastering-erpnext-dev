"""Remove parent_category and is_group DocField records from Asset Category"""
import frappe

def run():
    # Remove the stale DocField records that trigger NestedSet
    for fieldname in ('parent_category', 'is_group'):
        count = frappe.db.count('DocField', {
            'parent': 'Asset Category',
            'fieldname': fieldname
        })
        if count:
            frappe.db.delete('DocField', {
                'parent': 'Asset Category',
                'fieldname': fieldname
            })
            print(f"Deleted DocField: {fieldname}")
        else:
            print(f"DocField not found (already clean): {fieldname}")

    # Also drop the actual DB columns if they exist
    for col in ('parent_category', 'is_group'):
        try:
            frappe.db.sql(f"ALTER TABLE `tabAsset Category` DROP COLUMN `{col}`")
            print(f"Dropped column: {col}")
        except Exception as e:
            print(f"Column {col} already gone or error: {e}")

    frappe.db.commit()

    # Reload the DocType to clear cache
    frappe.reload_doctype('Asset Category')
    frappe.clear_cache(doctype='Asset Category')
    print("Done — Asset Category cleaned up")
