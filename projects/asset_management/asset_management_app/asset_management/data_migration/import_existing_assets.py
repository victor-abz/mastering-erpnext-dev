# -*- coding: utf-8 -*-
"""
Data Migration: Import Existing Assets
Chapter 11: Asset Management System

Run via bench console:
    bench --site <site> execute \
        asset_management.data_migration.import_existing_assets.run \
        --kwargs '{"csv_path": "/path/to/assets.csv"}'

Or as a one-off patch:
    bench --site <site> run-patch \
        asset_management.data_migration.import_existing_assets
"""

import csv
import frappe
from frappe import _
from frappe.utils import getdate, today


REQUIRED_COLUMNS = {'asset_name', 'asset_category', 'purchase_date', 'purchase_amount'}
BATCH_SIZE = 50  # commit every N rows to avoid losing all progress on crash


def run(csv_path=None):
	"""
	Entry point for the migration.
	Reads a CSV file and creates Asset documents for each row.
	Skips rows where an asset with the same serial_number already exists.
	Commits every BATCH_SIZE rows so partial progress is preserved on failure.
	"""
	if not csv_path:
		frappe.throw(_("csv_path is required"))

	results = {'created': 0, 'skipped': 0, 'errors': []}

	with open(csv_path, newline='', encoding='utf-8') as f:
		reader = csv.DictReader(f)
		_validate_columns(reader.fieldnames or [])

		for i, row in enumerate(reader, start=2):  # row 1 = header
			try:
				_import_row(row, results)
			except Exception as exc:
				results['errors'].append({'row': i, 'error': str(exc), 'data': dict(row)})
				frappe.db.rollback()

			# Commit in batches to preserve progress
			if (i - 1) % BATCH_SIZE == 0:
				frappe.db.commit()

	frappe.db.commit()  # final commit for the last partial batch

	frappe.logger().info(
		f"Asset import complete — created: {results['created']}, "
		f"skipped: {results['skipped']}, errors: {len(results['errors'])}"
	)

	if results['errors']:
		for err in results['errors']:
			frappe.log_error(
				message=f"Row {err['row']}: {err['error']}\nData: {err['data']}",
				title="Asset Import Error"
			)

	return results


def _validate_columns(fieldnames):
	missing = REQUIRED_COLUMNS - set(fieldnames)
	if missing:
		frappe.throw(_("CSV is missing required columns: {0}").format(', '.join(missing)))


def _import_row(row, results):
	"""Create a single Asset document from a CSV row dict."""
	serial_number = (row.get('serial_number') or '').strip()

	# Skip if already imported (idempotent)
	if serial_number and frappe.db.exists('Asset', {'serial_number': serial_number}):
		results['skipped'] += 1
		return

	# Skip if asset_name already exists
	asset_name = row['asset_name'].strip()
	if frappe.db.exists('Asset', {'asset_name': asset_name}):
		results['skipped'] += 1
		return

	try:
		purchase_amount = float(row['purchase_amount'])
	except (ValueError, TypeError):
		frappe.throw(_("Invalid purchase_amount '{0}' for asset '{1}'").format(
			row.get('purchase_amount'), asset_name
		))

	doc = frappe.get_doc({
		'doctype': 'Asset',
		'asset_name': asset_name,
		'asset_category': row['asset_category'].strip(),
		'item_code': (row.get('item_code') or '').strip() or None,
		'purchase_date': getdate(row['purchase_date'].strip()),
		'purchase_amount': purchase_amount,
		'serial_number': serial_number or None,
		'location': (row.get('location') or '').strip() or None,
		'status': (row.get('status') or 'Available').strip(),
	})

	# frappe.flags.in_import suppresses certain hook validations (e.g. stock checks)
	# Reset to False after each row so errors in one row don't affect the next
	frappe.flags.in_import = True
	try:
		doc.insert(ignore_permissions=True)
	finally:
		frappe.flags.in_import = False

	results['created'] += 1
