"""Check Asset Category DocType state in DB"""
import frappe

def run():
    # Check if parent_category field still exists in DB
    fields = frappe.db.get_all('DocField',
        filters={'parent': 'Asset Category'},
        fields=['fieldname', 'fieldtype'],
        order_by='idx'
    )
    print("Asset Category fields in DB:", [f.fieldname for f in fields])
    
    # Check is_tree flag
    is_tree = frappe.db.get_value('DocType', 'Asset Category', 'is_tree')
    print("is_tree:", is_tree)
    
    # Check if lft column exists in the actual table
    try:
        frappe.db.sql("SELECT lft FROM `tabAsset Category` LIMIT 1")
        print("lft column: EXISTS in table")
    except Exception as e:
        print("lft column: MISSING from table -", e)
    
    # Check if parent_category column exists
    try:
        frappe.db.sql("SELECT parent_category FROM `tabAsset Category` LIMIT 1")
        print("parent_category column: EXISTS in table")
    except Exception as e:
        print("parent_category column: MISSING -", e)
