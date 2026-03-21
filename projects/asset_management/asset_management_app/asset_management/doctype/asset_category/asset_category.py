# -*- coding: utf-8 -*-
"""
Asset Category DocType Controller
"""

import frappe
from frappe.model.document import Document


class AssetCategory(Document):
	"""Asset Category controller"""

	def validate(self):
		self.update_statistics()

	def update_statistics(self):
		"""Update category statistics"""
		self.total_assets = frappe.db.count('Asset', {'asset_category': self.name})

		total = frappe.db.sql(
			"SELECT SUM(current_value) FROM `tabAsset` WHERE asset_category = %s",
			self.name
		)
		self.total_value = total[0][0] if total and total[0][0] else 0
