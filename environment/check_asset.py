"""Check ERPNext hooks on Asset DocType"""
import frappe

def run():
    # Check what doc_events are registered for Asset across all apps
    all_hooks = frappe.get_hooks('doc_events')
    asset_hooks = all_hooks.get('Asset', {})
    print("doc_events for Asset:", asset_hooks)
    
    # Check if erpnext has its own Asset controller path
    import erpnext
    import os
    erpnext_path = os.path.dirname(erpnext.__file__)
    asset_controller = os.path.join(erpnext_path, 'assets', 'doctype', 'asset', 'asset.py')
    print(f"ERPNext asset controller exists: {os.path.exists(asset_controller)}")
    
    # Check the actual error by trying to insert
    try:
        frappe.flags.in_import = True
        doc = frappe.get_doc({
            'doctype': 'Asset',
            'asset_name': 'Debug Test 999',
            'asset_category': 'Smoke Test Equipment',
            'purchase_date': '2024-01-01',
            'purchase_amount': 100.0,
            'status': 'In Stock',
        })
        doc.insert(ignore_permissions=True)
        frappe.db.rollback()
        print("Insert succeeded")
    except Exception as e:
        import traceback
        print("Insert error:", e)
        traceback.print_exc()
    finally:
        frappe.flags.in_import = False
