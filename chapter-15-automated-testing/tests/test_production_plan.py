# -*- coding: utf-8 -*-
"""
Integration Tests for Production Plan
Chapter 15: Automated Testing
"""

import frappe
import unittest
from frappe.utils import today, add_days, getdate

class TestProductionPlan(unittest.TestCase):
	"""Integration tests for Production Plan DocType"""
	
	def setUp(self):
		"""Set up test data"""
		self.company = frappe.get_doc("Company", frappe.defaults.get_defaults().get("company"))
		
	def tearDown(self):
		"""Clean up test data"""
		frappe.db.rollback()
	
	def test_production_plan_creation(self):
		"""Test creating a production plan"""
		plan = frappe.get_doc({
			"doctype": "Production Plan",
			"company": self.company.name,
			"posting_date": today(),
			"from_date": today(),
			"to_date": add_days(today(), 30)
		})
		
		plan.insert()
		self.assertTrue(plan.name)
		self.assertEqual(plan.status, "Draft")
	
	def test_production_plan_items(self):
		"""Test adding items to production plan"""
		plan = frappe.get_doc({
			"doctype": "Production Plan",
			"company": self.company.name,
			"posting_date": today()
		})
		
		# Add item
		plan.append("po_items", {
			"item_code": "TEST-ITEM-001",
			"planned_qty": 100,
			"uom": "Nos"
		})
		
		plan.insert()
		self.assertEqual(len(plan.po_items), 1)
		self.assertEqual(plan.total_planned_qty, 100)
	
	def test_date_validation(self):
		"""Test date validation logic"""
		plan = frappe.get_doc({
			"doctype": "Production Plan",
			"company": self.company.name,
			"posting_date": today(),
			"from_date": add_days(today(), 10),
			"to_date": today()  # Invalid: to_date before from_date
		})
		
		with self.assertRaises(frappe.ValidationError):
			plan.insert()
