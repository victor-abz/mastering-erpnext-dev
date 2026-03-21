"""
Smoke test — run via:
  bench --site frontend execute environment.smoke_test.run
OR copy into container and run:
  bench --site frontend execute smoke_test.run
"""
import frappe


def run():
    print("=== Smoke Test ===")
    print("Installed apps:", frappe.get_installed_apps())

    for dt in ['Asset', 'Asset Category', 'Asset Assignment', 'Asset Maintenance', 'Production Plan']:
        exists = frappe.db.exists('DocType', dt)
        print(f"  DocType '{dt}': {'OK' if exists else 'MISSING'}")

    # Create a test Asset Category
    try:
        if not frappe.db.exists('Asset Category', 'Smoke Test Equipment'):
            cat = frappe.get_doc({
                'doctype': 'Asset Category',
                'category_name': 'Smoke Test Equipment',
                'depreciation_method': 'Straight Line',
                'total_number_of_depreciations': 5,
                'frequency_of_depreciation': 12,
            })
            cat.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"  Asset Category created: {cat.name}")
        else:
            print("  Asset Category already exists: Smoke Test Equipment")
    except Exception as e:
        print(f"  Asset Category ERROR: {e}")

    # Create a test Asset
    try:
        # Get first available company
        company = frappe.db.get_single_value('Global Defaults', 'default_company') or \
                  frappe.db.get_value('Company', {}, 'name')

        if not frappe.db.exists('Asset', {'asset_name': 'Smoke Test Laptop 001'}):
            asset = frappe.get_doc({
                'doctype': 'Asset',
                'asset_name': 'Smoke Test Laptop 001',
                'asset_category': 'Smoke Test Equipment',
                'company': company,
                'purchase_date': '2024-01-01',
                'purchase_amount': 1500.00,
                'status': 'Available',
            })
            asset.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"  Asset created: {asset.name} (company: {company})")
        else:
            print("  Asset already exists: Smoke Test Laptop 001")
    except Exception as e:
        print(f"  Asset ERROR: {e}")

    print("=== Done ===")
