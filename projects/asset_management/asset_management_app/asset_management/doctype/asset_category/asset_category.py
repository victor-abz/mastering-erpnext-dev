# -*- coding: utf-8 -*-
"""
Asset Category DocType Controller
"""

import frappe
from frappe.model.document import Document
from frappe.utils.nestedset import NestedSet

class AssetCategory(NestedSet):
	"""Asset Category with hierarchical structure"""
	
	nsm_parent_field = 'parent_category'
	
	def validate(self):
		"""Validate category data"""
		self.validate_group()
		self.update_statistics()
	
	def validate_group(self):
		"""Validate group category"""
		if self.is_group:
			# Group categories cannot have depreciation settings
			if self.depreciation_method or self.useful_life:
				frappe.msgprint("Group categories cannot have depreciation settings")
				self.depreciation_method = None
				self.useful_life = None
	
	def update_statistics(self):
		"""Update category statistics"""
		if not self.is_group:
			# Count assets in this category
			self.total_assets = frappe.db.count('Asset', {
				'asset_category': self.name
			})
			
			# Calculate total value
			total = frappe.db.sql("""
				SELECT SUM(current_value)
				FROM `tabAsset`
				WHERE asset_category = %s
			""", self.name)
			
			self.total_value = total[0][0] if total and total[0][0] else 0
