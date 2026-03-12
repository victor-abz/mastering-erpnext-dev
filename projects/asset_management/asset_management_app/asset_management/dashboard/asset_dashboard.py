# -*- coding: utf-8 -*-
"""
Asset Management Dashboard
Chapter 11: Real-time asset tracking dashboard
"""

import frappe
from frappe.utils import flt, getdate, today

@frappe.whitelist()
def get_dashboard_data():
	"""Get comprehensive dashboard data"""
	return {
		'summary': get_asset_summary(),
		'by_category': get_assets_by_category(),
		'by_status': get_assets_by_status(),
		'utilization': get_utilization_data(),
		'maintenance_due': get_maintenance_due_count(),
		'depreciation_trend': get_depreciation_trend()
	}

def get_asset_summary():
	"""Get overall asset summary"""
	summary = frappe.db.sql("""
		SELECT 
			COUNT(*) as total_assets,
			SUM(purchase_amount) as total_purchase_value,
			SUM(current_value) as total_current_value,
			SUM(accumulated_depreciation) as total_depreciation
		FROM `tabAsset`
		WHERE docstatus < 2
	""", as_dict=1)[0]
	
	return summary

def get_assets_by_category():
	"""Get asset distribution by category"""
	return frappe.db.sql("""
		SELECT 
			asset_category,
			COUNT(*) as count,
			SUM(current_value) as total_value
		FROM `tabAsset`
		WHERE docstatus < 2
		GROUP BY asset_category
		ORDER BY count DESC
		LIMIT 10
	""", as_dict=1)

def get_assets_by_status():
	"""Get asset distribution by status"""
	return frappe.db.sql("""
		SELECT 
			status,
			COUNT(*) as count
		FROM `tabAsset`
		WHERE docstatus < 2
		GROUP BY status
	""", as_dict=1)

def get_utilization_data():
	"""Get asset utilization statistics"""
	total_assets = frappe.db.count('Asset', {'status': ['in', ['Available', 'Assigned']]})
	assigned_assets = frappe.db.count('Asset', {'status': 'Assigned'})
	
	utilization_rate = (assigned_assets / total_assets * 100) if total_assets > 0 else 0
	
	return {
		'total_assets': total_assets,
		'assigned_assets': assigned_assets,
		'available_assets': total_assets - assigned_assets,
		'utilization_rate': utilization_rate
	}

def get_maintenance_due_count():
	"""Get count of assets with maintenance due"""
	from frappe.utils import add_days
	
	count = frappe.db.sql("""
		SELECT COUNT(DISTINCT asset)
		FROM `tabAsset Maintenance`
		WHERE next_maintenance_date <= %s
		AND maintenance_status != 'Completed'
	""", add_days(today(), 7))[0][0]
	
	return count or 0

def get_depreciation_trend():
	"""Get depreciation trend for last 12 months"""
	from frappe.utils import add_months
	
	data = []
	for i in range(12, 0, -1):
		month_date = add_months(today(), -i)
		
		total_depreciation = frappe.db.sql("""
			SELECT SUM(accumulated_depreciation)
			FROM `tabAsset`
			WHERE purchase_date <= %s
		""", month_date)[0][0] or 0
		
		data.append({
			'month': month_date.strftime('%b %Y'),
			'depreciation': flt(total_depreciation)
		})
	
	return data
