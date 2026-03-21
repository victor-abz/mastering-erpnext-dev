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
		"""Check if asset is available and not simultaneously assigned"""
		if self.asset:
			asset_status = frappe.db.get_value('Asset', self.asset, 'status')

			if asset_status != 'Available' and self.is_new():
				frappe.throw(_("Asset {0} is not available for assignment").format(self.asset))

			# Check for overlapping assignments (simultaneous assignment prevention)
			# An overlap exists when another active assignment's date range intersects ours.
			# Condition: existing.from_date <= our.to_date  AND  existing.to_date >= our.from_date
			to_date = self.to_date or '2099-12-31'
			overlapping = frappe.db.sql("""
				SELECT name, employee, from_date, to_date
				FROM `tabAsset Assignment`
				WHERE asset = %(asset)s
				  AND docstatus = 1
				  AND name != %(name)s
				  AND from_date <= %(to_date)s
				  AND COALESCE(to_date, '2099-12-31') >= %(from_date)s
				LIMIT 1
			""", {
				'asset': self.asset,
				'name': self.name or '',
				'from_date': self.from_date,
				'to_date': to_date
			}, as_dict=True)

			if overlapping:
				conflict = overlapping[0]
				frappe.throw(_(
					"Asset {0} is already assigned to {1} from {2} to {3}. "
					"Simultaneous assignments are not allowed."
				).format(
					self.asset,
					conflict.employee,
					conflict.from_date,
					conflict.to_date or _('open-ended')
				))
	
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
