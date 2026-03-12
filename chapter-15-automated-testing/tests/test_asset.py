# -*- coding: utf-8 -*-
"""
Asset DocType Tests
Chapter 15: Automated Testing
"""

import frappe
import unittest
from frappe.utils import today, add_days, getdate

class TestAsset(unittest.TestCase):
	"""Test cases for Asset DocType"""
	
	def setUp(self):
		"""Set up test data"""
		self.create_test_category()
		self.create_test_item()
	
	def tearDown(self):
		"""Clean up test data"""
		frappe.db.rollback()
	
	def create_test_category(self):
		"""Create test asset category"""
		if not frappe.db.exists('Asset Category', 'Test Category'):
			category = frappe.get_doc({
				'doctype': 'Asset Category',
				'asset_category_name': 'Test Category',
				'depreciation_method': 'Straight Line',
				'useful_life': 5
			})
			category.insert()
	
	def create_test_item(self):
		"""Create test item"""
		if not frappe.db.exists('Item', 'TEST-ASSET-001'):
			item = frappe.get_doc({
				'doctype': 'Item',
				'item_code': 'TEST-ASSET-001',
				'item_name': 'Test Asset Item',
				'item_group': 'Products',
				'stock_uom': 'Nos',
				'is_stock_item': 1
			})
			item.insert()
	
	def test_asset_creation(self):
		"""Test basic asset creation"""
		asset = frappe.get_doc({
			'doctype': 'Asset',
			'asset_name': 'Test Laptop',
			'asset_category': 'Test Category',
			'item_code': 'TEST-ASSET-001',
			'purchase_date': today(),
			'purchase_amount': 1000.00,
			'status': 'Available'
		})
		asset.insert()
		
		self.assertTrue(frappe.db.exists('Asset', asset.name))
		self.assertEqual(asset.asset_name, 'Test Laptop')
		self.assertEqual(asset.purchase_amount, 1000.00)
	
	def test_asset_validation_required_fields(self):
		"""Test required field validation"""
		asset = frappe.get_doc({
			'doctype': 'Asset',
			'asset_category': 'Test Category'
		})
		
		with self.assertRaises(frappe.MandatoryError):
			asset.insert()
	
	def test_asset_validation_dates(self):
		"""Test date validation"""
		future_date = add_days(today(), 30)
		
		asset = frappe.get_doc({
			'doctype': 'Asset',
			'asset_name': 'Test Asset',
			'asset_category': 'Test Category',
			'purchase_date': future_date,
			'purchase_amount': 1000.00
		})
		
		with self.assertRaises(frappe.ValidationError):
			asset.insert()
	
	def test_asset_validation_amounts(self):
		"""Test amount validation"""
		asset = frappe.get_doc({
			'doctype': 'Asset',
			'asset_name': 'Test Asset',
			'asset_category': 'Test Category',
			'purchase_date': today(),
			'purchase_amount': -100.00
		})
		
		with self.assertRaises(frappe.ValidationError):
			asset.insert()
	
	def test_asset_depreciation_calculation(self):
		"""Test depreciation calculation"""
		past_date = add_days(today(), -365)
		
		asset = frappe.get_doc({
			'doctype': 'Asset',
			'asset_name': 'Test Asset',
			'asset_category': 'Test Category',
			'purchase_date': past_date,
			'purchase_amount': 1000.00,
			'depreciation_method': 'Straight Line',
			'useful_life': 5
		})
		asset.insert()
		
		# After 1 year, depreciation should be ~200 (1000/5)
		self.assertGreater(asset.accumulated_depreciation, 0)
		self.assertLess(asset.accumulated_depreciation, asset.purchase_amount)
	
	def test_asset_current_value(self):
		"""Test current value calculation"""
		asset = frappe.get_doc({
			'doctype': 'Asset',
			'asset_name': 'Test Asset',
			'asset_category': 'Test Category',
			'purchase_date': today(),
			'purchase_amount': 1000.00
		})
		asset.insert()
		
		expected_value = asset.purchase_amount - (asset.accumulated_depreciation or 0)
		self.assertEqual(asset.current_value, expected_value)
	
	def test_asset_status_change(self):
		"""Test asset status workflow"""
		asset = frappe.get_doc({
			'doctype': 'Asset',
			'asset_name': 'Test Asset',
			'asset_category': 'Test Category',
			'purchase_date': today(),
			'purchase_amount': 1000.00,
			'status': 'Available'
		})
		asset.insert()
		
		# Change status
		asset.status = 'In Use'
		asset.save()
		
		saved_asset = frappe.get_doc('Asset', asset.name)
		self.assertEqual(saved_asset.status, 'In Use')

def run_tests():
	"""Run all asset tests"""
	suite = unittest.TestLoader().loadTestsFromTestCase(TestAsset)
	unittest.TextTestRunner(verbosity=2).run(suite)
