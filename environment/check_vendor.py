import frappe
frappe.init(site="frontend")
frappe.connect()
result = frappe.db.sql("SHOW TABLES LIKE 'tabVendor'")
print("tabVendor exists:", bool(result))
if result:
    cols = frappe.db.sql("DESCRIBE tabVendor")
    for c in cols:
        print(c)
frappe.destroy()
