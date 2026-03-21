import frappe
frappe.init(site='frontend')
frappe.connect()
frappe.set_user('Administrator')

if not frappe.db.exists('Asset Category', 'Test Category'):
    frappe.get_doc({
        'doctype': 'Asset Category',
        'category_name': 'Test Category',
        'depreciation_method': 'Straight Line',
        'useful_life': 5
    }).insert()

from frappe.utils import today
asset = frappe.get_doc({
    'doctype': 'Asset',
    'asset_name': 'Delete Test Asset',
    'asset_category': 'Test Category',
    'purchase_date': today(),
    'purchase_amount': 1000.00,
    'status': 'In Use'
})
asset.insert()
print('Inserted:', asset.name, 'status:', asset.status)
print('DB status:', frappe.db.get_value('Asset', asset.name, 'status'))

try:
    asset.delete()
    print('ERROR: delete succeeded, should have raised')
except Exception as e:
    print('Got exception (expected):', type(e).__name__, str(e)[:100])

frappe.db.rollback()
