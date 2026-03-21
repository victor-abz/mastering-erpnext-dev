# -*- coding: utf-8 -*-
"""
Daily scheduled tasks for Asset Management
"""

import frappe
from frappe.utils import today, add_days, getdate

def check_maintenance_due():
	"""Check for assets with maintenance due and send notifications"""
	from frappe.utils import add_days
	
	# Get assets with maintenance due in next 7 days
	maintenance_due = frappe.db.sql("""
		SELECT 
			am.name,
			am.asset,
			a.asset_name,
			am.next_maintenance_date,
			am.maintenance_type
		FROM `tabAsset Maintenance` am
		INNER JOIN `tabAsset` a ON a.name = am.asset
		WHERE am.next_maintenance_date <= %s
		AND am.next_maintenance_date >= %s
		AND am.maintenance_status != 'Completed'
	""", (add_days(today(), 7), today()), as_dict=1)
	
	if maintenance_due:
		# Send notification to Asset Managers
		users = frappe.get_all('Has Role', 
			filters={'role': 'Asset Manager'},
			fields=['parent']
		)
		
		for user in users:
			frappe.sendmail(
				recipients=[user.parent],
				subject='Asset Maintenance Due',
				message=get_maintenance_notification_html(maintenance_due)
			)

def update_asset_values():
	"""Update current values for all assets based on depreciation"""
	assets = frappe.get_all('Asset',
		filters={'docstatus': 1},
		fields=['name']
	)
	
	for asset in assets:
		doc = frappe.get_doc('Asset', asset.name)
		doc._compute_depreciation()
		doc._compute_current_value()
		doc.db_update()
	
	frappe.db.commit()

def get_maintenance_notification_html(maintenance_list):
	"""Generate HTML for maintenance notification"""
	html = """
	<h3>Assets Requiring Maintenance</h3>
	<table border="1" cellpadding="5" cellspacing="0">
		<tr>
			<th>Asset</th>
			<th>Asset Name</th>
			<th>Maintenance Type</th>
			<th>Due Date</th>
		</tr>
	"""
	
	for item in maintenance_list:
		html += f"""
		<tr>
			<td>{item.asset}</td>
			<td>{item.asset_name}</td>
			<td>{item.maintenance_type}</td>
			<td>{item.next_maintenance_date}</td>
		</tr>
		"""
	
	html += "</table>"
	return html
