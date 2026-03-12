# -*- coding: utf-8 -*-
"""
API Method Tests
Chapter 15: Automated Testing
"""

import frappe
import unittest
from frappe.utils import today

class TestAPIMethods(unittest.TestCase):
	"""Test cases for whitelisted API methods"""
	
	def setUp(self):
		"""Set up test environment"""
		self.create_test_data()
	
	def tearDown(self):
		"""Clean up"""
		frappe.db.rollback()
	
	def create_test_data(self):
		"""Create test data"""
		# Create test customer
		if not frappe.db.exists('Customer', 'TEST-CUST-001'):
			customer = frappe.get_doc({
				'doctype': 'Customer',
				'customer_name': 'Test Customer',
				'customer_type': 'Individual',
				'customer_group': 'Individual',
				'territory': 'All Territories'
			})
			customer.insert()
	
	def test_get_customer_balance(self):
		"""Test get customer balance API"""
		from erpnext.accounts.utils import get_balance_on
		
		balance = get_balance_on(
			party_type='Customer',
			party='TEST-CUST-001',
			date=today()
		)
		
		self.assertIsInstance(balance, (int, float))
		self.assertGreaterEqual(balance, 0)
	
	def test_api_authentication(self):
		"""Test API requires authentication"""
		# Set guest user
		frappe.set_user('Guest')
		
		# Try to access protected method
		with self.assertRaises(frappe.PermissionError):
			frappe.call('frappe.client.get_list', doctype='Customer')
		
		# Reset to admin
		frappe.set_user('Administrator')
	
	def test_api_parameter_validation(self):
		"""Test API parameter validation"""
		# Test missing required parameter
		with self.assertRaises(Exception):
			frappe.call('frappe.client.get', doctype='Customer')
	
	def test_api_response_format(self):
		"""Test API response format"""
		response = frappe.call(
			'frappe.client.get',
			doctype='Customer',
			name='TEST-CUST-001'
		)
		
		self.assertIsInstance(response, dict)
		self.assertIn('name', response)
		self.assertIn('customer_name', response)

def run_tests():
	"""Run all API tests"""
	suite = unittest.TestLoader().loadTestsFromTestCase(TestAPIMethods)
	unittest.TextTestRunner(verbosity=2).run(suite)
