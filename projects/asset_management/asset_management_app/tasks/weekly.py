# -*- coding: utf-8 -*-
"""
Weekly scheduled tasks for Asset Management
"""

import frappe
from frappe.utils import today, add_days, getdate

def generate_utilization_report():
	"""Generate weekly asset utilization report"""
	from frappe.utils import add_days
	
	to_date = today()
	from_date = add_days(to_date, -7)
	
	# Get utilization data
	data = frappe.db.sql("""
		SELECT 
			a.asset_category,
			COUNT(DISTINCT a.name) as total_assets,
			COUNT(DISTINCT CASE WHEN a.status = 'Assigned' THEN a.name END) as assigned_assets,
			SUM(a.current_value) as total_value
		FROM `tabAsset` a
		WHERE a.docstatus < 2
		GROUP BY a.asset_category
	""", as_dict=1)
	
	# Send report to Asset Managers
	users = frappe.get_all('Has Role',
		filters={'role': 'Asset Manager'},
		fields=['parent']
	)
	
	for user in users:
		frappe.sendmail(
			recipients=[user.parent],
			subject=f'Weekly Asset Utilization Report - {today()}',
			message=get_utilization_report_html(data, from_date, to_date)
		)

def get_utilization_report_html(data, from_date, to_date):
	"""Generate HTML for utilization report"""
	html = f"""
	<h3>Asset Utilization Report</h3>
	<p>Period: {from_date} to {to_date}</p>
	<table border="1" cellpadding="5" cellspacing="0">
		<tr>
			<th>Category</th>
			<th>Total Assets</th>
			<th>Assigned</th>
			<th>Utilization %</th>
			<th>Total Value</th>
		</tr>
	"""
	
	for row in data:
		utilization = (row.assigned_assets / row.total_assets * 100) if row.total_assets > 0 else 0
		html += f"""
		<tr>
			<td>{row.asset_category}</td>
			<td>{row.total_assets}</td>
			<td>{row.assigned_assets}</td>
			<td>{utilization:.1f}%</td>
			<td>{frappe.utils.fmt_money(row.total_value)}</td>
		</tr>
		"""
	
	html += "</table>"
	return html
