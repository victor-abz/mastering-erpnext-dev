import frappe
from frappe.utils import today

if not frappe.db.exists('Asset Category', 'Test Category'):
    frappe.get_doc({
        'doctype': 'Asset Category',
        'category_name': 'Test Category',
        'depreciation_method': 'Straight Line',
        'useful_life': 5
    }).insert()

asset = frappe.get_doc({
    'doctype': 'Asset',
    'asset_name': 'Test Laptop',
    'asset_category': 'Test Category',
    'item_code': 'TEST-ASSET-001',
    'purchase_date': today(),
    'purchase_amount': 1000.00,
    'status': 'In Stock'
})

print('depreciation_method before insert:', repr(asset.depreciation_method))
print('useful_life before insert:', repr(asset.useful_life))
print('type(useful_life):', type(asset.useful_life))

frappe.db.rollback()
