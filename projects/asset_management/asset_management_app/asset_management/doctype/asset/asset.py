# -*- coding: utf-8 -*-
"""
Asset DocType Controller
Chapter 11: Asset Management System
"""

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, today, add_days
from frappe import _

class Asset(Document):
	"""Asset management controller with complete lifecycle"""
	
	def validate(self):
		"""Validate asset data"""
		self.validate_dates()
		self.validate_amounts()
		self.validate_category()
		self.set_asset_name()
	
	def validate_dates(self):
		"""Validate date fields"""
		if self.purchase_date and getdate(self.purchase_date) > getdate(today()):
			frappe.throw(_("Purchase date cannot be in the future"))
		
		if self.available_from_date and self.purchase_date:
			if getdate(self.available_from_date) < getdate(self.purchase_date):
				frappe.throw(_("Available from date cannot be before purchase date"))
	
	def validate_amounts(self):
		"""Validate amount fields"""
		if self.purchase_amount and self.purchase_amount <= 0:
			frappe.throw(_("Purchase amount must be greater than zero"))
		
		if self.current_value and self.current_value < 0:
			frappe.throw(_("Current value cannot be negative"))
	
	def validate_category(self):
		"""Validate and set category defaults"""
		if self.asset_category:
			category = frappe.get_doc('Asset Category', self.asset_category)
			
			if not self.depreciation_method and category.depreciation_method:
				self.depreciation_method = category.depreciation_method
			
			if not self.useful_life and category.useful_life:
				self.useful_life = category.useful_life
	
	def set_asset_name(self):
		"""Set asset name if not provided"""
		if not self.asset_name and self.item_code:
			self.asset_name = frappe.db.get_value('Item', self.item_code, 'item_name')
	
	def before_save(self):
		"""Calculate values before saving"""
		self.calculate_depreciation()
		self.calculate_current_value()
	
	def calculate_depreciation(self):
		"""Calculate accumulated depreciation"""
		if not self.purchase_amount or not self.purchase_date:
			return
		
		if self.depreciation_method == 'Straight Line' and self.useful_life:
			days_since_purchase = (getdate(today()) - getdate(self.purchase_date)).days
			annual_depreciation = self.purchase_amount / self.useful_life
			self.accumulated_depreciation = min(
				(annual_depreciation * days_since_purchase) / 365,
				self.purchase_amount
			)
	
	def calculate_current_value(self):
		"""Calculate current asset value"""
		if self.purchase_amount:
			self.current_value = self.purchase_amount - (self.accumulated_depreciation or 0)
	
	def on_update(self):
		"""After save operations"""
		self.update_category_statistics()
	
	def update_category_statistics(self):
		"""Update asset category statistics"""
		if self.asset_category:
			frappe.db.sql("""
				UPDATE `tabAsset Category`
				SET total_assets = (
					SELECT COUNT(*) FROM `tabAsset` 
					WHERE asset_category = %(category)s
				)
				WHERE name = %(category)s
			""", {'category': self.asset_category})

@frappe.whitelist()
def get_available_assets(asset_category=None):
	"""Get list of available assets"""
	filters = {'status': 'Available'}
	if asset_category:
		filters['asset_category'] = asset_category
	
	return frappe.get_all('Asset',
		filters=filters,
		fields=['name', 'asset_name', 'asset_category', 'current_value']
	)

@frappe.whitelist()
def get_asset_utilization(asset_name, from_date, to_date):
	"""Calculate asset utilization for period"""
	assignments = frappe.get_all('Asset Assignment',
		filters={
			'asset': asset_name,
			'from_date': ['<=', to_date],
			'to_date': ['>=', from_date]
		},
		fields=['from_date', 'to_date']
	)
	
	total_days = (getdate(to_date) - getdate(from_date)).days + 1
	utilized_days = 0
	
	for assignment in assignments:
		start = max(getdate(from_date), getdate(assignment.from_date))
		end = min(getdate(to_date), getdate(assignment.to_date))
		utilized_days += (end - start).days + 1
	
	return {
		'total_days': total_days,
		'utilized_days': utilized_days,
		'utilization_percentage': (utilized_days / total_days * 100) if total_days > 0 else 0
	}
