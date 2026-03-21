# -*- coding: utf-8 -*-
"""
Asset Maintenance DocType Controller
"""

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_months, add_days
from frappe import _

class AssetMaintenance(Document):
	"""Asset maintenance tracking"""
	
	def validate(self):
		"""Validate maintenance record"""
		self.validate_dates()
		self.calculate_next_maintenance()
	
	def validate_dates(self):
		"""Validate date fields"""
		if self.next_maintenance_date and self.maintenance_date:
			if getdate(self.next_maintenance_date) <= getdate(self.maintenance_date):
				frappe.throw(_("Next maintenance date must be after maintenance date"))
	
	def calculate_next_maintenance(self):
		"""Calculate next maintenance date based on frequency"""
		if self.maintenance_status == "Completed" and not self.next_maintenance_date:
			asset = frappe.get_doc('Asset', self.asset)
			if asset.asset_category:
				category = frappe.get_doc('Asset Category', asset.asset_category)
				
				if category.enable_maintenance and category.maintenance_frequency:
					frequency_map = {
						'Monthly': 1,
						'Quarterly': 3,
						'Half-Yearly': 6,
						'Yearly': 12
					}
					
					months = frequency_map.get(category.maintenance_frequency, 3)
					self.next_maintenance_date = getdate(add_months(self.maintenance_date, months))
	
	def on_update(self):
		"""After save operations"""
		if self.maintenance_status == "Completed":
			self.update_asset_maintenance_date()
	
	def update_asset_maintenance_date(self):
		"""Update last maintenance date on asset"""
		frappe.db.set_value('Asset', self.asset, 
			'last_maintenance_date', self.maintenance_date)

@frappe.whitelist()
def get_maintenance_due():
	"""Get assets with maintenance due"""
	from frappe.utils import today, add_days
	
	return frappe.db.sql("""
		SELECT 
			a.name as asset,
			a.asset_name,
			a.asset_category,
			am.next_maintenance_date
		FROM `tabAsset` a
		LEFT JOIN `tabAsset Maintenance` am ON am.asset = a.name
		WHERE am.next_maintenance_date <= %s
		AND am.maintenance_status != 'Completed'
		ORDER BY am.next_maintenance_date
	""", add_days(today(), 7), as_dict=1)
