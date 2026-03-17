# -*- coding: utf-8 -*-
"""
Vendor Portal REST API
Chapter 13: Vendor Portal - REST API Development
"""

import frappe
from frappe import _
from frappe.utils import today, getdate
import hashlib
import time

def validate_api_token(token):
	"""Validate API token and return vendor information"""
	try:
		# Check if token exists in cache
		vendor_name = frappe.cache().get(f"vendor_token:{token}")
		
		if not vendor_name:
			frappe.throw(_("Invalid or expired token"), frappe.AuthenticationError)
		
		# Verify vendor still exists and is active
		vendor = frappe.db.get_value('Vendor', 
			{'name': vendor_name, 'status': 'Active'},
			['name', 'vendor_name', 'email'],
			as_dict=1
		)
		
		if not vendor:
			# Remove invalid token from cache
			frappe.cache().delete(f"vendor_token:{token}")
			frappe.throw(_("Vendor account not found or inactive"), frappe.AuthenticationError)
		
		return vendor
		
	except Exception as e:
		frappe.log_error(f"Token validation failed: {str(e)}")
		frappe.throw(_("Authentication failed"), frappe.AuthenticationError)

def rate_limit_check(vendor_name, action='api_call'):
	"""Implement rate limiting for API calls"""
	try:
		cache_key = f"rate_limit:{vendor_name}:{action}"
		current_count = frappe.cache().get(cache_key) or 0
		
		# Allow 100 calls per hour per vendor
		if current_count >= 100:
			frappe.throw(_("Rate limit exceeded. Please try again later."), frappe.PermissionError)
		
		# Increment counter with 1 hour expiry
		frappe.cache().setex(cache_key, current_count + 1, 3600)
		
	except Exception as e:
		frappe.log_error(f"Rate limiting check failed: {str(e)}")

@frappe.whitelist(allow_guest=True)
def authenticate(api_key, api_secret):
	"""Authenticate vendor using API credentials with enhanced security"""
	try:
		# Input validation
		if not api_key or not api_secret:
			frappe.throw(_("API key and secret are required"), frappe.ValidationError)
		
		if len(api_key) < 10 or len(api_secret) < 10:
			frappe.throw(_("Invalid API credentials format"), frappe.ValidationError)
		
		# Rate limiting for authentication attempts
		client_ip = frappe.local.request_ip
		auth_attempts_key = f"auth_attempts:{client_ip}"
		attempts = frappe.cache().get(auth_attempts_key) or 0
		
		if attempts >= 5:
			frappe.throw(_("Too many authentication attempts. Please try again later."), frappe.PermissionError)
		
		# Find vendor with matching credentials
		vendor = frappe.db.get_value('Vendor',
			{'api_key': api_key, 'api_secret': api_secret, 'status': 'Active'},
			['name', 'vendor_name', 'email'],
			as_dict=1
		)
		
		if not vendor:
			# Increment failed attempts counter
			frappe.cache().setex(auth_attempts_key, attempts + 1, 300)  # 5 minutes
			frappe.throw(_("Invalid API credentials"), frappe.AuthenticationError)
		
		# Generate secure session token
		import secrets
		token = secrets.token_urlsafe(32)
		
		# Store token in cache with vendor data and timestamp
		token_data = {
			'vendor_name': vendor.name,
			'vendor_email': vendor.email,
			'created_at': time.time()
		}
		frappe.cache().setex(f"vendor_token:{token}", token_data, 86400)  # 24 hours
		
		# Clear authentication attempts on success
		frappe.cache().delete(auth_attempts_key)
		
		# Log successful authentication
		frappe.logger().info(f"Vendor {vendor.name} authenticated successfully")
		
		return {
			'success': True,
			'token': token,
			'vendor': {
				'name': vendor.name,
				'vendor_name': vendor.vendor_name,
				'email': vendor.email
			},
			'expires_in': 86400
		}
		
	except Exception as e:
		frappe.log_error(f"Authentication failed: {str(e)}")
		raise

@frappe.whitelist()
def get_purchase_orders(vendor, status=None, token=None):
	"""Get purchase orders for vendor with proper authentication"""
	try:
		# Validate token
		if not token:
			frappe.throw(_("Authentication token required"), frappe.AuthenticationError)
		
		vendor_info = validate_api_token(token)
		
		# Verify vendor matches token
		if vendor_info['name'] != vendor:
			frappe.throw(_("Access denied: Vendor mismatch"), frappe.PermissionError)
		
		# Rate limiting
		rate_limit_check(vendor, 'get_purchase_orders')
		
		# Build filters
		filters = {'supplier': vendor, 'docstatus': 1}
		
		if status:
			# Validate status values
			valid_statuses = ['To Receive', 'Partially Received', 'Received', 'Closed']
			if status not in valid_statuses:
				frappe.throw(_("Invalid status value"), frappe.ValidationError)
			filters['status'] = status
		
		# Get purchase orders with additional security fields
		orders = frappe.get_all('Purchase Order',
			filters=filters,
			fields=[
				'name', 
				'transaction_date', 
				'schedule_date', 
				'grand_total', 
				'status',
				'currency',
				'perceived_total_currency'
			],
			order_by='transaction_date desc',
			limit=100  # Prevent data dumping
		)
		
		# Log API access
		frappe.logger().info(f"Vendor {vendor} accessed {len(orders)} purchase orders")
		
		return {
			'success': True,
			'data': orders,
			'total_count': len(orders)
		}
		
	except Exception as e:
		frappe.log_error(f"Get purchase orders failed for vendor {vendor}: {str(e)}")
		frappe.throw(_("Failed to retrieve purchase orders"), frappe.PermissionError)
