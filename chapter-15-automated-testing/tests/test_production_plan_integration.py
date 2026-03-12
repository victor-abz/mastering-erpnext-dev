# -*- coding: utf-8 -*-
"""
Integration Tests for Production Planning Workflow
Chapter 15: Automated Testing - Integration Tests
"""

import frappe
import unittest
from frappe.utils import today, add_days

class TestProductionPlanningIntegration(unittest.TestCase):
	"""Integration tests for complete production planning workflow"""
	
	@classmethod
	def setUpClass(cls):
		"""Set up test data once for all tests"""
		cls.company = frappe.defaults.get_defaults().get("company")
		cls.create_test_items()
		cls.create_test_bom()
	
	@classmethod
	def create_test_items(cls):
		"""Create test items for production"""
		# Create finished good
		if not frappe.db.exists("Item", "TEST-FG-001"):
			frappe.get_doc({
				"doctype": "Item",
				"item_code": "TEST-FG-001",
				"item_name": "Test Finished Good",
				"item_group": "Products",
				"stock_uom": "Nos"
			}).insert(ignore_permissions=True)
		
		# Create raw material
		if not frappe.db.exists("Item", "TEST-RM-001"):
			frappe.get_doc({
				"doctype": "Item",
				"item_code": "TEST-RM-001",
				"item_name": "Test Raw Material",
				"item_group": "Raw Material",
				"stock_uom": "Kg"
			}).insert(ignore_permissions=True)
	
	@classmethod
	def create_test_bom(cls):
		"""Create test BOM"""
		if not frappe.db.exists("BOM", {"item": "TEST-FG-001"}):
			bom = frappe.get_doc({
				"doctype": "BOM",
				"item": "TEST-FG-001",
				"quantity": 1,
				"is_active": 1,
				"is_default": 1
			})
			
			bom.append("items", {
				"item_code": "TEST-RM-001",
				"qty": 2,
				"uom": "Kg"
			})
			
			bom.insert(ignore_permissions=True)
			bom.submit()
	
	def tearDown(self):
		"""Clean up after each test"""
		frappe.db.rollback()
	
	def test_sales_order_to_production_plan(self):
		"""Test creating production plan from sales order"""
		# Create sales order
		so = frappe.get_doc({
			"doctype": "Sales Order",
			"customer": "_Test Customer",
			"company": self.company,
			"transaction_date": today(),
			"delivery_date": add_days(today(), 7)
		})
		
		so.append("items", {
			"item_code": "TEST-FG-001",
			"qty": 10,
			"rate": 1000
		})
		
		so.insert()
		so.submit()
		
		# Create production plan
		plan = frappe.get_doc({
			"doctype": "Production Plan",
			"company": self.company,
			"posting_date": today(),
			"get_items_from": "Sales Order"
		})
		
		plan.append("sales_orders", {
			"sales_order": so.name
		})
		
		plan.insert()
		
		# Verify plan created
		self.assertTrue(plan.name)
		self.assertEqual(plan.get_items_from, "Sales Order")
	
	def test_bom_explosion(self):
		"""Test BOM explosion for material requirements"""
		plan = frappe.get_doc({
			"doctype": "Production Plan",
			"company": self.company,
			"posting_date": today()
		})
		
		plan.append("po_items", {
			"item_code": "TEST-FG-001",
			"planned_qty": 10,
			"uom": "Nos"
		})
		
		plan.insert()
		
		# Test BOM explosion
		from production_planning_app.production_planning.doctype.production_plan.production_plan import explode_bom
		
		raw_materials = explode_bom(plan.name)
		
		# Verify raw materials calculated
		self.assertTrue(len(raw_materials) > 0)
		
		# Find our test raw material
		test_rm = next((rm for rm in raw_materials if rm['item_code'] == 'TEST-RM-001'), None)
		self.assertIsNotNone(test_rm)
		self.assertEqual(test_rm['required_qty'], 20)  # 10 FG * 2 RM per FG
	
	def test_production_plan_submission(self):
		"""Test production plan submission workflow"""
		plan = frappe.get_doc({
			"doctype": "Production Plan",
			"company": self.company,
			"posting_date": today()
		})
		
		plan.append("po_items", {
			"item_code": "TEST-FG-001",
			"planned_qty": 5,
			"uom": "Nos"
		})
		
		plan.insert()
		self.assertEqual(plan.docstatus, 0)
		self.assertEqual(plan.status, "Draft")
		
		plan.submit()
		self.assertEqual(plan.docstatus, 1)
		self.assertEqual(plan.status, "Submitted")
	
	def test_completion_percentage_calculation(self):
		"""Test completion percentage calculation"""
		plan = frappe.get_doc({
			"doctype": "Production Plan",
			"company": self.company,
			"posting_date": today()
		})
		
		plan.append("po_items", {
			"item_code": "TEST-FG-001",
			"planned_qty": 100,
			"produced_qty": 50,
			"uom": "Nos"
		})
		
		plan.insert()
		
		# Verify calculation
		self.assertEqual(plan.total_planned_qty, 100)
		self.assertEqual(plan.total_produced_qty, 50)
		self.assertEqual(plan.completion_percentage, 50)
