# -*- coding: utf-8 -*-
"""Vendor DocType Controller"""

import frappe
from frappe.model.document import Document
from frappe import _


class Vendor(Document):
	"""External vendor with API access credentials"""

	def before_insert(self):
		"""Auto-generate API key/secret if not provided"""
		if not self.api_key:
			self.api_key = frappe.generate_hash(length=20)
		if not self.api_secret:
			self.api_secret = frappe.generate_hash(length=20)

	def validate(self):
		if not self.vendor_name:
			frappe.throw(_("Vendor Name is required"))
