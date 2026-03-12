# -*- coding: utf-8 -*-
"""
Row-Level Permission Examples
Chapter 9: Permissions System
"""

import frappe

def get_permission_query_conditions(user):
	"""
	Return SQL conditions for filtering records based on user permissions
	Used in: permission_query_conditions hook
	"""
	if not user:
		user = frappe.session.user
	
	# System Manager can see everything
	if 'System Manager' in frappe.get_roles(user):
		return ""
	
	# Department-based filtering
	user_departments = frappe.get_all('User Permission',
		filters={
			'user': user,
			'allow': 'Department'
		},
		pluck='for_value'
	)
	
	if user_departments:
		departments_str = ', '.join([f"'{d}'" for d in user_departments])
		return f"`tabAsset`.department IN ({departments_str})"
	
	# If no departments, user can only see their own records
	return f"`tabAsset`.owner = '{user}'"

def has_permission(doc, user):
	"""
	Check if user has permission for specific document
	Used in: has_permission hook
	"""
	if not user:
		user = frappe.session.user
	
	# System Manager has all permissions
	if 'System Manager' in frappe.get_roles(user):
		return True
	
	# Asset Manager can access all assets
	if 'Asset Manager' in frappe.get_roles(user):
		return True
	
	# Check if user is custodian
	if doc.custodian:
		custodian_user = frappe.db.get_value('Employee', doc.custodian, 'user_id')
		if custodian_user == user:
			return True
	
	# Check department access
	if doc.department:
		has_dept_access = frappe.db.exists('User Permission', {
			'user': user,
			'allow': 'Department',
			'for_value': doc.department
		})
		if has_dept_access:
			return True
	
	# Check if user is owner
	if doc.owner == user:
		return True
	
	return False
