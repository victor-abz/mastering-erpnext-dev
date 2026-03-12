# -*- coding: utf-8 -*-
"""
Asset Assignment DocType Controller
Chapter 11: Asset Management System
"""

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today
from frappe import _

class AssetAssignment(Document):
	"""Asset assignment controller"""
	
	def validate(self):
		"""Validate assignment"""
		self.validate_dates()
		self.validate_asset_availability()
		self.validate_employee()
	
	def validate_dates(self):
		"""Validate date fields"""
		if self.from_date and getdate(self.from_date) > getdate(today()):
			frappe.throw(_("From date cannot be in the future"))
		
		if self.to_date and self.from_date:
			if getdate(self.to_date) < getdate(self.from_date):
				frappe.throw(_("To date cannot be before from date"))
	
	def validate_asset_availability(self):
		"""Check if asset is available"""
		if self.asset:
			asset_status = frappe.db.get_value('Asset', self.asset, 'status')
			
			if asset_status != 'Available' and self.is_new():
				frappe.throw(_("Asset {0} is not available for assignment").format(self.asset))
			
			# Check for overlapping assignments
			overlapping = frappe.db.exists('Asset Assignment', {
				'asset': self.asset,
				'docstatus': 1,
				'from_date': ['<=', self.to_date or '2099-12-31'],
				'to_date': ['>=', self.from_date],
				'name': ['!=', self.name]
			})
			
			if overlapping:
				frappe.throw(_("Asset {0} is already assigned for this period").format(self.asset))
	
	def validate_employee(self):
		"""Validate employee exists and is active"""
		if self.employee:
			employee_status = frappe.db.get_value('Employee', self.employee, 'status')
			if employee_status != 'Active':
				frappe.throw(_("Employee {0} is not active").format(self.employee))
	
	def on_submit(self):
		"""Update asset status on assignment"""
		if self.asset:
			frappe.db.set_value('Asset', self.asset, 'status', 'In Use')
			frappe.db.set_value('Asset', self.asset, 'custodian', self.employee)
	
	def on_cancel(self):
		"""Revert asset status on cancellation"""
		if self.asset:
			frappe.db.set_value('Asset', self.asset, 'status', 'Available')
			frappe.db.set_value('Asset', self.asset, 'custodian', None)

@frappe.whitelist()
def get_employee_assets(employee):
	"""Get all assets assigned to an employee"""
	return frappe.get_all('Asset Assignment',
		filters={
			'employee': employee,
			'docstatus': 1,
			'to_date': ['>=', today()]
		},
		fields=['asset', 'asset_name', 'from_date', 'to_date']
	)
