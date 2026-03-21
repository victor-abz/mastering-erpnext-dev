# -*- coding: utf-8 -*-
"""
Sales Order utilities for Production Planning
"""

import frappe
from frappe import _


def create_production_plan_from_sales_order(doc, method=None):
	"""
	Hook: called on Sales Order on_submit.
	Creates a draft Production Plan linked to the submitted Sales Order.
	"""
	try:
		plan = frappe.get_doc({
			"doctype": "Production Plan",
			"company": doc.company,
			"posting_date": doc.transaction_date,
			"sales_order": doc.name,
			"status": "Draft"
		})

		for item in doc.items:
			if frappe.db.get_value("Item", item.item_code, "is_stock_item"):
				plan.append("po_items", {
					"item_code": item.item_code,
					"planned_qty": item.qty,
					"uom": item.uom
				})

		if plan.po_items:
			plan.insert(ignore_permissions=True)
			frappe.logger().info(
				f"Production Plan {plan.name} created from Sales Order {doc.name}"
			)

	except Exception as e:
		frappe.log_error(
			f"Failed to create Production Plan from Sales Order {doc.name}: {e}"
		)
