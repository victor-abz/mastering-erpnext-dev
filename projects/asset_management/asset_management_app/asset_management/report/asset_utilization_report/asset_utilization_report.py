# -*- coding: utf-8 -*-
"""
Asset Utilization Report
Chapter 11: Analyze asset usage patterns
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
	"""Execute report"""
	columns = get_columns()
	data = get_data(filters)
	
	return columns, data

def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "asset",
			"label": _("Asset"),
			"fieldtype": "Link",
			"options": "Asset",
			"width": 150
		},
		{
			"fieldname": "asset_name",
			"label": _("Asset Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "asset_category",
			"label": _("Category"),
			"fieldtype": "Link",
			"options": "Asset Category",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "total_days",
			"label": _("Total Days"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "assigned_days",
			"label": _("Assigned Days"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "utilization_rate",
			"label": _("Utilization %"),
			"fieldtype": "Percent",
			"width": 120
		},
		{
			"fieldname": "current_value",
			"label": _("Current Value"),
			"fieldtype": "Currency",
			"width": 120
		}
	]

def get_data(filters):
	"""Get report data"""
	from_date = filters.get('from_date')
	to_date = filters.get('to_date')
	asset_category = filters.get('asset_category')
	
	# Build conditions
	conditions = []
	if asset_category:
		conditions.append(f"a.asset_category = '{asset_category}'")
	
	where_clause = " AND " + " AND ".join(conditions) if conditions else ""
	
	# Get assets with assignment data
	data = frappe.db.sql(f"""
		SELECT 
			a.name as asset,
			a.asset_name,
			a.asset_category,
			a.status,
			a.current_value,
			COUNT(DISTINCT aa.name) as assignment_count,
			SUM(DATEDIFF(
				LEAST(aa.to_date, %(to_date)s),
				GREATEST(aa.from_date, %(from_date)s)
			) + 1) as assigned_days
		FROM `tabAsset` a
		LEFT JOIN `tabAsset Assignment` aa ON aa.asset = a.name
			AND aa.from_date <= %(to_date)s
			AND aa.to_date >= %(from_date)s
			AND aa.docstatus = 1
		WHERE a.docstatus < 2
		{where_clause}
		GROUP BY a.name
		ORDER BY a.asset_category, a.asset_name
	""", {
		'from_date': from_date,
		'to_date': to_date
	}, as_dict=1)
	
	# Calculate utilization
	total_days = (getdate(to_date) - getdate(from_date)).days + 1
	
	for row in data:
		row['total_days'] = total_days
		row['assigned_days'] = row.get('assigned_days') or 0
		row['utilization_rate'] = (row['assigned_days'] / total_days * 100) if total_days > 0 else 0
	
	return data
