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
		if not frappe.db.exists("Vendor", "TEST-VENDOR-001"):
			vendor = frappe.get_doc({
				"doctype": "Vendor",
				"vendor_name": "Test Vendor",
				"api_key": "test_api_key_123",
				"api_secret": "test_api_secret_456",
				"webhook_url": "https://example.com/webhook"
			})
			vendor.insert(ignore_permissions=True)
			cls.vendor_name = vendor.name
		else:
			cls.vendor_name = "TEST-VENDOR-001"
	
	@classmethod
	def create_test_purchase_order(cls):
		"""Create test purchase order"""
		if not frappe.db.exists("Purchase Order", {"supplier": cls.vendor_name}):
			po = frappe.get_doc({
				"doctype": "Purchase Order",
				"supplier": cls.vendor_name,
				"company": frappe.defaults.get_defaults().get("company"),
				"transaction_date": today(),
				"schedule_date": today()
			})
			
			po.append("items", {
				"item_code": "TEST-ITEM-001",
				"qty": 10,
				"rate": 100
			})
			
			po.insert(ignore_permissions=True)
			po.submit()
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
		
		# Store token in cache
		frappe.cache().setex(
			f"vendor_token:{auth_result['token']}", 
			self.vendor_name, 
			86400
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
			self.vendor_name, 
			86400
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
			self.vendor_name, 
			86400
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
			"TEST-VENDOR-002", 
			86400
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
