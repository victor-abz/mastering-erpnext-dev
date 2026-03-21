# -*- coding: utf-8 -*-
"""
End-to-End Tests for Vendor Portal API
Chapter 15: Automated Testing - E2E Tests
"""

import frappe
import unittest
import json
from frappe.utils import today

class TestVendorPortalE2E(unittest.TestCase):
	"""End-to-end tests for Vendor Portal API"""
	
	@classmethod
	def setUpClass(cls):
		"""Set up test vendor and data"""
		cls.create_test_vendor()
		cls.create_test_purchase_order()
	
	@classmethod
	def create_test_vendor(cls):
		"""Create test vendor with API credentials"""
		if not frappe.db.exists("Vendor", "Test Vendor"):
			vendor = frappe.get_doc({
				"doctype": "Vendor",
				"vendor_name": "Test Vendor",
				"api_key": "test_api_key_123",
				"api_secret": "test_api_secret_456",
				"webhook_url": "https://example.com/webhook",
				"status": "Active"
			})
			vendor.insert(ignore_permissions=True)
			frappe.db.commit()
			cls.vendor_name = vendor.name
		else:
			cls.vendor_name = frappe.db.get_value("Vendor", {"vendor_name": "Test Vendor"}, "name") or "Test Vendor"

	@classmethod
	def create_test_purchase_order(cls):
		"""Create test purchase order"""
		existing = frappe.db.get_value("Purchase Order", {"supplier": cls.vendor_name}, "name")
		if existing:
			cls.po_name = existing
			return

		# Ensure a supplier exists with the same name as our vendor
		if not frappe.db.exists("Supplier", cls.vendor_name):
			supplier = frappe.get_doc({
				"doctype": "Supplier",
				"supplier_name": cls.vendor_name,
				"supplier_group": "All Supplier Groups",
				"supplier_type": "Company"
			})
			supplier.insert(ignore_permissions=True)
			frappe.db.commit()

		company = frappe.defaults.get_defaults().get("company")
		po = frappe.get_doc({
			"doctype": "Purchase Order",
			"supplier": cls.vendor_name,
			"company": company,
			"transaction_date": today(),
			"schedule_date": today(),
			"currency": "USD"
		})
		po.append("items", {
			"item_code": "PERF-TEST-ITEM",
			"qty": 10,
			"rate": 100,
			"schedule_date": today(),
			"uom": "Nos"
		})
		po.insert(ignore_permissions=True, ignore_links=True)
		po.submit()
		frappe.db.commit()
		cls.po_name = po.name
	
	def tearDown(self):
		"""Clean up after each test"""
		frappe.db.rollback()
	
	def test_e2e_authentication_flow(self):
		"""Test complete authentication flow"""
		from vendor_portal_app.vendor_portal.api.vendor import authenticate
		
		# Test successful authentication
		result = authenticate(
			api_key="test_api_key_123",
			api_secret="test_api_secret_456"
		)
		
		self.assertTrue(result['success'])
		self.assertIn('token', result)
		self.assertIn('vendor', result)
		self.assertEqual(result['vendor']['name'], self.vendor_name)
		
		# Store token for subsequent tests
		self.token = result['token']
	
	def test_e2e_invalid_authentication(self):
		"""Test authentication with invalid credentials"""
		from vendor_portal_app.vendor_portal.api.vendor import authenticate
		
		with self.assertRaises(frappe.AuthenticationError):
			authenticate(
				api_key="invalid_key",
				api_secret="invalid_secret"
			)
	
	def test_e2e_get_purchase_orders(self):
		"""Test retrieving purchase orders"""
		# First authenticate
		from vendor_portal_app.vendor_portal.api.vendor import authenticate, get_purchase_orders
		
		auth_result = authenticate(
			api_key="test_api_key_123",
			api_secret="test_api_secret_456"
		)
		
		# Store token in cache (v16: setex(key, ttl, value))
		frappe.cache().setex(
			f"vendor_token:{auth_result['token']}", 
			86400,
			self.vendor_name
		)
		
		# Get purchase orders
		result = get_purchase_orders(vendor=self.vendor_name)
		
		self.assertTrue(result['success'])
		self.assertIn('data', result)
		self.assertTrue(len(result['data']) > 0)
	
	def test_e2e_get_purchase_order_details(self):
		"""Test retrieving specific purchase order details"""
		from vendor_portal_app.vendor_portal.api.vendor import authenticate
		from vendor_portal_app.vendor_portal.api.purchase_order import get_purchase_order_details
		
		# Authenticate
		auth_result = authenticate(
			api_key="test_api_key_123",
			api_secret="test_api_secret_456"
		)
		
		# Store token
		frappe.cache().setex(
			f"vendor_token:{auth_result['token']}", 
			86400,
			self.vendor_name
		)
		
		# Set request header for authentication
		frappe.local.request = frappe._dict({
			"headers": {
				"Authorization": f"Bearer {auth_result['token']}"
			}
		})
		
		# Get PO details
		result = get_purchase_order_details(purchase_order=self.po_name)
		
		self.assertTrue(result['success'])
		self.assertIn('data', result)
		self.assertEqual(result['data']['name'], self.po_name)
		self.assertEqual(result['data']['supplier'], self.vendor_name)
		self.assertTrue(len(result['data']['items']) > 0)
	
	def test_e2e_acknowledge_purchase_order(self):
		"""Test acknowledging a purchase order"""
		from vendor_portal_app.vendor_portal.api.vendor import authenticate
		from vendor_portal_app.vendor_portal.api.purchase_order import acknowledge_purchase_order
		
		# Authenticate
		auth_result = authenticate(
			api_key="test_api_key_123",
			api_secret="test_api_secret_456"
		)
		
		# Store token
		frappe.cache().setex(
			f"vendor_token:{auth_result['token']}", 
			86400,
			self.vendor_name
		)
		
		# Set request header
		frappe.local.request = frappe._dict({
			"headers": {
				"Authorization": f"Bearer {auth_result['token']}"
			}
		})
		
		# Acknowledge PO
		result = acknowledge_purchase_order(
			purchase_order=self.po_name,
			acknowledgement_date=today(),
			notes="Order received and will be processed"
		)
		
		self.assertTrue(result['success'])
		self.assertIn('message', result)
	
	def test_e2e_unauthorized_access(self):
		"""Test accessing PO without proper authentication"""
		from vendor_portal_app.vendor_portal.api.purchase_order import get_purchase_order_details
		
		# Set invalid token
		frappe.local.request = frappe._dict({
			"headers": {
				"Authorization": "Bearer invalid_token"
			}
		})
		
		with self.assertRaises(frappe.AuthenticationError):
			get_purchase_order_details(purchase_order=self.po_name)
	
	def test_e2e_cross_vendor_access(self):
		"""Test that vendor cannot access another vendor's PO"""
		# Create another vendor
		if not frappe.db.exists("Vendor", "TEST-VENDOR-002"):
			vendor2 = frappe.get_doc({
				"doctype": "Vendor",
				"vendor_name": "Test Vendor 2",
				"api_key": "test_api_key_789",
				"api_secret": "test_api_secret_012"
			})
			vendor2.insert(ignore_permissions=True)
		
		# Authenticate as vendor 2
		from vendor_portal_app.vendor_portal.api.vendor import authenticate
		from vendor_portal_app.vendor_portal.api.purchase_order import get_purchase_order_details
		
		auth_result = authenticate(
			api_key="test_api_key_789",
			api_secret="test_api_secret_012"
		)
		
		# Store token for vendor 2
		frappe.cache().setex(
			f"vendor_token:{auth_result['token']}", 
			86400,
			"TEST-VENDOR-002"
		)
		
		# Set request header
		frappe.local.request = frappe._dict({
			"headers": {
				"Authorization": f"Bearer {auth_result['token']}"
			}
		})
		
		# Try to access vendor 1's PO
		with self.assertRaises(frappe.PermissionError):
			get_purchase_order_details(purchase_order=self.po_name)
