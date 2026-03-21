# -*- coding: utf-8 -*-
"""
Monthly scheduled tasks for Asset Management
"""

import frappe
from frappe.utils import today, add_months, getdate

def calculate_depreciation():
	"""Calculate and record monthly depreciation for all assets"""
	assets = frappe.get_all('Asset',
		filters={
			'docstatus': 1,
			'status': ['!=', 'Disposed']
		},
		fields=['name', 'purchase_amount', 'purchase_date', 'depreciation_method', 'useful_life']
	)
	
	for asset in assets:
		if asset.depreciation_method and asset.useful_life:
			doc = frappe.get_doc('Asset', asset.name)
			
			# Calculate depreciation
			doc._compute_depreciation()
			doc._compute_current_value()
			
			# Save without triggering full validation
			doc.db_update()
			
			# Create depreciation entry (if you have a separate DocType for tracking)
			# create_depreciation_entry(doc)
	
	frappe.db.commit()
	
	# Send summary report
	send_depreciation_summary()

def send_depreciation_summary():
	"""Send monthly depreciation summary to finance team"""
	summary = frappe.db.sql("""
		SELECT 
			asset_category,
			COUNT(*) as asset_count,
			SUM(purchase_amount) as total_purchase_value,
			SUM(accumulated_depreciation) as total_depreciation,
			SUM(current_value) as total_current_value
		FROM `tabAsset`
		WHERE docstatus = 1
		GROUP BY asset_category
	""", as_dict=1)
	
	# Get finance users
	users = frappe.get_all('Has Role',
		filters={'role': ['in', ['Accounts Manager', 'Asset Manager']]},
		fields=['parent']
	)
	
	for user in users:
		frappe.sendmail(
			recipients=[user.parent],
			subject=f'Monthly Depreciation Summary - {today()}',
			message=get_depreciation_summary_html(summary)
		)

def get_depreciation_summary_html(summary):
	"""Generate HTML for depreciation summary"""
	html = f"""
	<h3>Monthly Depreciation Summary</h3>
	<p>Date: {today()}</p>
	<table border="1" cellpadding="5" cellspacing="0">
		<tr>
			<th>Category</th>
			<th>Assets</th>
			<th>Purchase Value</th>
			<th>Accumulated Depreciation</th>
			<th>Current Value</th>
		</tr>
	"""
	
	total_purchase = 0
	total_depreciation = 0
	total_current = 0
	
	for row in summary:
		html += f"""
		<tr>
			<td>{row.asset_category}</td>
			<td>{row.asset_count}</td>
			<td>{frappe.utils.fmt_money(row.total_purchase_value)}</td>
			<td>{frappe.utils.fmt_money(row.total_depreciation)}</td>
			<td>{frappe.utils.fmt_money(row.total_current_value)}</td>
		</tr>
		"""
		total_purchase += row.total_purchase_value or 0
		total_depreciation += row.total_depreciation or 0
		total_current += row.total_current_value or 0
	
	html += f"""
		<tr style="font-weight: bold;">
			<td>TOTAL</td>
			<td></td>
			<td>{frappe.utils.fmt_money(total_purchase)}</td>
			<td>{frappe.utils.fmt_money(total_depreciation)}</td>
			<td>{frappe.utils.fmt_money(total_current)}</td>
		</tr>
	</table>
	"""
	
	return html
