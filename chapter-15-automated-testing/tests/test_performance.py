# -*- coding: utf-8 -*-
"""
Performance Tests
Chapter 15: Automated Testing - Performance Tests
"""

import frappe
import unittest
import time
from frappe.utils import today, add_days

class TestPerformance(unittest.TestCase):
	"""Performance tests for critical operations"""
	
	def setUp(self):
		"""Set up test data"""
		self.company = frappe.defaults.get_defaults().get("company")
	
	def tearDown(self):
		"""Clean up"""
		frappe.db.rollback()
	
	def test_asset_list_query_performance(self):
		"""Test asset list query performance"""
		start_time = time.time()
		
		# Query assets
		assets = frappe.get_all('Asset',
			filters={'docstatus': ['<', 2]},
			fields=['name', 'asset_name', 'status', 'current_value'],
			limit=100
		)
		
		end_time = time.time()
		execution_time = end_time - start_time
		
		# Should complete in under 1 second
		self.assertLess(execution_time, 1.0, 
			f"Asset list query took {execution_time:.2f}s, expected < 1.0s")
	
	def test_dashboard_data_performance(self):
		"""Test dashboard data retrieval performance"""
		from asset_management_app.asset_management.dashboard.asset_dashboard import get_dashboard_data
		
		start_time = time.time()
		
		# Get dashboard data
		data = get_dashboard_data()
		
		end_time = time.time()
		execution_time = end_time - start_time
		
		# Should complete in under 2 seconds
		self.assertLess(execution_time, 2.0,
			f"Dashboard query took {execution_time:.2f}s, expected < 2.0s")
		
		# Verify data structure
		self.assertIn('summary', data)
		self.assertIn('by_category', data)
		self.assertIn('utilization', data)
	
	def test_bom_explosion_performance(self):
		"""Test BOM explosion performance"""
		# Create test production plan
		plan = frappe.get_doc({
			"doctype": "Production Plan",
			"company": self.company,
			"posting_date": today()
		})
		
		# Add multiple items
		for i in range(10):
			plan.append("po_items", {
				"item_code": f"TEST-ITEM-{i:03d}",
				"planned_qty": 100,
				"uom": "Nos"
			})
		
		plan.insert()
		
		start_time = time.time()
		
		# Explode BOM
		from production_planning_app.production_planning.doctype.production_plan.production_plan import explode_bom
		raw_materials = explode_bom(plan.name)
		
		end_time = time.time()
		execution_time = end_time - start_time
		
		# Should complete in under 3 seconds for 10 items
		self.assertLess(execution_time, 3.0,
			f"BOM explosion took {execution_time:.2f}s, expected < 3.0s")
	
	def test_bulk_asset_creation_performance(self):
		"""Test bulk asset creation performance"""
		start_time = time.time()
		
		# Create 50 assets
		assets_created = []
		for i in range(50):
			asset = frappe.get_doc({
				"doctype": "Asset",
				"asset_name": f"Performance Test Asset {i}",
				"item_code": "TEST-ITEM-001",
				"asset_category": "Test Category",
				"purchase_date": today(),
				"purchase_amount": 10000,
				"company": self.company
			})
			asset.insert()
			assets_created.append(asset.name)
		
		end_time = time.time()
		execution_time = end_time - start_time
		
		# Should complete in under 10 seconds for 50 assets
		self.assertLess(execution_time, 10.0,
			f"Bulk creation took {execution_time:.2f}s, expected < 10.0s")
		
		# Calculate average time per asset
		avg_time = execution_time / 50
		self.assertLess(avg_time, 0.2,
			f"Average time per asset: {avg_time:.3f}s, expected < 0.2s")
	
	def test_report_generation_performance(self):
		"""Test report generation performance"""
		from asset_management_app.asset_management.report.asset_utilization_report.asset_utilization_report import execute
		
		filters = {
			'from_date': add_days(today(), -30),
			'to_date': today()
		}
		
		start_time = time.time()
		
		# Generate report
		columns, data = execute(filters)
		
		end_time = time.time()
		execution_time = end_time - start_time
		
		# Should complete in under 2 seconds
		self.assertLess(execution_time, 2.0,
			f"Report generation took {execution_time:.2f}s, expected < 2.0s")
	
	def test_api_authentication_performance(self):
		"""Test API authentication performance"""
		from vendor_portal_app.vendor_portal.api.vendor import authenticate
		
		# Create test vendor if not exists
		if not frappe.db.exists("Vendor", "PERF-TEST-VENDOR"):
			vendor = frappe.get_doc({
				"doctype": "Vendor",
				"vendor_name": "Performance Test Vendor",
				"api_key": "perf_test_key",
				"api_secret": "perf_test_secret"
			})
			vendor.insert(ignore_permissions=True)
		
		start_time = time.time()
		
		# Authenticate 10 times
		for i in range(10):
			result = authenticate(
				api_key="perf_test_key",
				api_secret="perf_test_secret"
			)
		
		end_time = time.time()
		execution_time = end_time - start_time
		
		# Should complete in under 1 second for 10 authentications
		self.assertLess(execution_time, 1.0,
			f"10 authentications took {execution_time:.2f}s, expected < 1.0s")
		
		# Calculate average time per authentication
		avg_time = execution_time / 10
		self.assertLess(avg_time, 0.1,
			f"Average auth time: {avg_time:.3f}s, expected < 0.1s")
	
	def test_database_query_optimization(self):
		"""Test that queries use proper indexes"""
		# Test asset query with index
		start_time = time.time()
		
		frappe.db.sql("""
			SELECT name, asset_name, status
			FROM `tabAsset`
			WHERE status = 'Available'
			AND asset_category = 'Test Category'
			LIMIT 100
		""")
		
		end_time = time.time()
		execution_time = end_time - start_time
		
		# Should be very fast with proper indexing
		self.assertLess(execution_time, 0.1,
			f"Indexed query took {execution_time:.3f}s, expected < 0.1s")
