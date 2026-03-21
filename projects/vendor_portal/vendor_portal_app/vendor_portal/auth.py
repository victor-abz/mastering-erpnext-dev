# -*- coding: utf-8 -*-
"""
Custom authentication helpers for Vendor Portal
"""

import frappe


def get_logged_user():
	"""
	Override for frappe.auth.get_logged_user.
	Falls back to the standard implementation so normal desk users are unaffected.
	"""
	return frappe.session.user
