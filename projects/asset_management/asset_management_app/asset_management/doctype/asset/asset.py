# -*- coding: utf-8 -*-
"""
Asset DocType Controller
Chapter 11: Asset Management System
"""

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, today, add_days
from frappe import _
from typing import Optional

# Status transitions that are allowed
VALID_STATUS_TRANSITIONS = {
	'Available':         {'In Stock', 'In Use', 'Under Maintenance', 'Scrapped'},
	'In Stock':          {'Available', 'In Use', 'Under Maintenance', 'Scrapped'},
	'In Use':            {'Available', 'In Stock', 'Under Maintenance', 'Scrapped'},
	'Under Maintenance': {'Available', 'In Stock', 'In Use'},
	'Scrapped':          set(),  # terminal state
}


class Asset(Document):
	"""Asset management controller with complete lifecycle"""

	def before_insert(self):
		"""Set defaults required by ERPNext hooks"""
		if not getattr(self, 'company', None):
			self.company = (
				frappe.db.get_single_value('Global Defaults', 'default_company')
				or frappe.db.get_value('Company', {}, 'name')
			)
		# Auto-generate asset_id if not set
		if not getattr(self, 'asset_id', None):
			self.asset_id = frappe.generate_hash(length=8).upper()

	def validate(self):
		"""Validate asset data"""
		self.validate_dates()
		# Check useful_life=0 BEFORE category inheritance overrides it
		self._check_useful_life_before_category_inherit()
		self.validate_category()
		self.validate_amounts()
		self.validate_duplicate_serial()
		self.validate_status_transition()
		self.validate_location()
		self.set_asset_name()

	def _check_useful_life_before_category_inherit(self):
		"""Raise early if useful_life is explicitly 0 with Straight Line depreciation"""
		method = getattr(self, 'depreciation_method', None)
		useful_life = flt(getattr(self, 'useful_life', None) or 0)
		if method == 'Straight Line' and useful_life == 0 and getattr(self, 'purchase_amount', None):
			frappe.throw(_("Useful life must be greater than zero for Straight Line depreciation"))

	def validate_dates(self):
		"""Validate date fields"""
		if self.purchase_date and getdate(self.purchase_date) > getdate(today()):
			frappe.throw(_("Purchase date cannot be in the future"))

		commissioning = getattr(self, 'commissioning_date', None)
		if commissioning and self.purchase_date:
			if getdate(commissioning) < getdate(self.purchase_date):
				frappe.throw(_("Commissioning date cannot be before purchase date"))

		available = getattr(self, 'available_from_date', None)
		if available and self.purchase_date:
			if getdate(available) < getdate(self.purchase_date):
				frappe.throw(_("Available from date cannot be before purchase date"))

	def validate_amounts(self):
		"""Validate amount fields"""
		if self.purchase_amount is not None and flt(self.purchase_amount) <= 0:
			frappe.throw(_("Purchase amount must be greater than zero"))

		salvage = flt(getattr(self, 'salvage_value', None) or 0)
		if salvage and salvage > flt(self.purchase_amount):
			frappe.throw(_("Salvage value cannot be greater than purchase amount"))

		if self.current_value and flt(self.current_value) < 0:
			frappe.throw(_("Current value cannot be negative"))

	def validate_category(self):
		"""Validate and inherit category defaults"""
		if self.asset_category:
			category = frappe.get_doc('Asset Category', self.asset_category)
			if not self.depreciation_method and category.depreciation_method:
				self.depreciation_method = category.depreciation_method
			# Only inherit useful_life if it was not explicitly set (None or 0 means not set)
			# But we can't distinguish 0 from "not set" for Int fields, so only inherit if 0
			if not flt(getattr(self, 'useful_life', None) or 0) and category.useful_life:
				self.useful_life = category.useful_life

	def validate_duplicate_serial(self):
		"""Prevent duplicate serial numbers"""
		serial = (getattr(self, 'serial_number', None) or '').strip()
		if not serial:
			return
		existing = frappe.db.get_value('Asset', {'serial_number': serial, 'docstatus': ['!=', 2]}, 'name')
		if existing and existing != self.name:
			frappe.throw(_("Asset with serial number {0} already exists: {1}").format(serial, existing))

		# Check for duplicate asset with same item code
		existing_asset = frappe.db.exists("Asset", {
			"item_code": self.item_code,
			"docstatus": ["!=", 2]  # Exclude cancelled assets
		})
		
		if existing_asset and existing_asset != self.name:
			frappe.throw(_("Asset with Item Code {0} already exists: {1}").format(
				self.item_code, existing_asset
			), frappe.DuplicateEntryError)
	
		# v16: Enhanced duplicate check with bulk operations
		if hasattr(self, '_bulk_mode') and self._bulk_mode:
			# Use bulk operation for better performance
			duplicates = frappe.db.get_all("Asset", {
				"item_code": self.item_code,
				"docstatus": ["!=", 2]
			}, fields=["name", "asset_name"])
			
			if duplicates:
				frappe.throw(_("Multiple assets found with Item Code {0}").format(
					self.item_code
				), frappe.DuplicateEntryError)

	def validate_status_transition(self):
		"""Enforce valid status transitions on existing documents"""
		if self.is_new():
			return
		old_status = frappe.db.get_value('Asset', self.name, 'status')
		if not old_status or old_status == self.status:
			return
		allowed = VALID_STATUS_TRANSITIONS.get(old_status, set())
		if self.status not in allowed:
			frappe.throw(_(
				"Cannot transition asset status from {0} to {1}"
			).format(old_status, self.status))

	def validate_location(self):
		"""Validate location exists if provided"""
		loc = getattr(self, 'location', None)
		if loc and not frappe.db.exists('Location', loc):
			frappe.throw(_("Location {0} does not exist").format(loc))

	def set_asset_name(self):
		"""Set asset name from item if not provided"""
		if not getattr(self, 'asset_name', None) and getattr(self, 'item_code', None):
			self.asset_name = frappe.db.get_value('Item', self.item_code, 'item_name')

	def before_save(self):
		"""Calculate values before saving"""
		self._compute_depreciation()
		self._compute_current_value()

	def _compute_depreciation(self):
		"""Calculate accumulated depreciation"""
		if not self.purchase_amount or not self.purchase_date:
			return

		purchase_amount = flt(self.purchase_amount)
		salvage_value = flt(getattr(self, 'salvage_value', None) or 0)
		depreciable_amount = purchase_amount - salvage_value

		method = getattr(self, 'depreciation_method', None)
		useful_life = flt(getattr(self, 'useful_life', None) or 0)

		if method == 'Straight Line' and useful_life > 0:
			days_since_purchase = (getdate(today()) - getdate(self.purchase_date)).days
			annual_depreciation = depreciable_amount / useful_life
			raw = (annual_depreciation * days_since_purchase) / 365
			# Cap at depreciable amount (never depreciate below salvage value)
			self.accumulated_depreciation = min(raw, depreciable_amount)

		elif method == 'Written Down Value':
			rate = flt(getattr(self, 'depreciation_rate', None) or 0)
			if rate > 0:
				years = (getdate(today()) - getdate(self.purchase_date)).days / 365
				current = purchase_amount * ((1 - rate / 100) ** years)
				self.accumulated_depreciation = min(
					purchase_amount - current,
					purchase_amount  # never exceed purchase amount
				)

	def _compute_current_value(self):
		"""Calculate current asset value, floored at salvage_value"""
		if self.purchase_amount:
			salvage_value = flt(getattr(self, 'salvage_value', None) or 0)
			raw = flt(self.purchase_amount) - flt(self.accumulated_depreciation or 0)
			self.current_value = max(raw, salvage_value)

	def on_trash(self):
		"""Prevent deletion of assets that are in use"""
		if getattr(self, 'status', None) == 'In Use':
			frappe.throw(_("Cannot delete an asset that is currently In Use"))

	def before_delete(self):
		"""Prevent deletion of assets that are in use (alias for on_trash)"""
		if getattr(self, 'status', None) == 'In Use':
			frappe.throw(_("Cannot delete an asset that is currently In Use"))

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
					WHERE asset_category = %(category)s AND docstatus != 2
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
	"""Calculate asset utilization for a period"""
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
	for a in assignments:
		start = max(getdate(from_date), getdate(a.from_date))
		end = min(getdate(to_date), getdate(a.to_date))
		utilized_days += (end - start).days + 1
	return {
		'total_days': total_days,
		'utilized_days': utilized_days,
		'utilization_percentage': (utilized_days / total_days * 100) if total_days > 0 else 0
	}
