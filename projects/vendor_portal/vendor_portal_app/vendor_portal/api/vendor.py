# -*- coding: utf-8 -*-
"""
Vendor Portal REST API
Chapter 13: Vendor Portal - REST API Development

Enhanced for ERPNext v16 with modern security practices,
rate limiting, and comprehensive error handling.
"""

import frappe
from frappe import _
from frappe.utils import today, getdate, now_datetime
import hashlib
import time
import secrets
from typing import Dict, Any, Optional, List, Union

# v16: Enhanced imports for modern security
from frappe.utils.rate_limiter import rate_limit
from frappe.utils.caching import redis_cache

def validate_api_token(token: str) -> Dict[str, Any]:
	"""Validate API token and return vendor information"""
	try:
		# Token data is stored as a dict in cache (set by authenticate())
		token_data = redis_cache.get(f"vendor_token:{token}")
		token_data = frappe.cache().get(f"vendor_token:{token}")
		
		if not token_data:
			frappe.throw(_("Invalid or expired token"), frappe.AuthenticationError)
		
		# token_data is a dict: {'vendor_name': ..., 'vendor_email': ..., 'created_at': ...}
		vendor_name = token_data.get('vendor_name') if isinstance(token_data, dict) else token_data
		
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

def rate_limit_check(vendor_name: str, action: str = 'api_call') -> None:
	"""Implement rate limiting for API calls"""
	try:
		cache_key = f"rate_limit:{vendor_name}:{action}"
		current_count = frappe.cache().get(cache_key) or 0
		
		# Allow 100 calls per hour per vendor
		if current_count >= 100:
			frappe.throw(_("Rate limit exceeded. Please try again later."), frappe.PermissionError)
		
		# Increment counter with 1 hour expiry (v16: setex(key, ttl, value))
		frappe.cache().setex(cache_key, 3600, current_count + 1)
		
	except Exception as e:
		frappe.log_error(f"Rate limiting check failed: {str(e)}")

@frappe.whitelist(allow_guest=True)
def authenticate(api_key: str, api_secret: str) -> Dict[str, Any]:
	"""Authenticate vendor using API credentials with enhanced security"""
	try:
		# Input validation
		if not api_key or not api_secret:
			frappe.throw(_("API key and secret are required"), frappe.ValidationError)
		
		if len(api_key) < 10 or len(api_secret) < 10:
			frappe.throw(_("Invalid API credentials format"), frappe.ValidationError)
		
		# Rate limiting for authentication attempts
		client_ip = getattr(frappe.local, 'request_ip', '127.0.0.1')
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
			# Increment failed attempts counter (v16: setex(key, ttl, value))
			frappe.cache().setex(auth_attempts_key, 300, attempts + 1)  # 5 minutes
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
		frappe.cache().setex(f"vendor_token:{token}", 86400, token_data)  # 24 hours (v16: key, ttl, value)
		
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
def get_purchase_orders(vendor: str, status: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
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
				'base_grand_total',
				'status',
				'currency'
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

# ─────────────────────────────────────────────────────────────────────────────
# Webhook delivery with HMAC-SHA256 signature verification
# ─────────────────────────────────────────────────────────────────────────────

import hmac
import hashlib
import json as _json


def send_webhook(vendor: str, event: str, payload: Dict[str, Any]) -> bool:
	"""
	Send a signed webhook to the vendor's registered endpoint.

	The request includes an `X-Webhook-Signature` header containing an
	HMAC-SHA256 digest of the raw JSON body, keyed with the vendor's
	`webhook_secret`.  Recipients should verify this signature before
	processing the payload:

	    import hmac, hashlib
	    expected = hmac.new(secret.encode(), body_bytes, hashlib.sha256).hexdigest()
	    assert hmac.compare_digest(expected, request.headers['X-Webhook-Signature'])

	Frappe's built-in API key/secret auth (User > API Access) is an
	alternative for server-to-server calls where the vendor can make
	authenticated requests directly to /api/method/... using the
	Authorization: token <api_key>:<api_secret> header.
	"""
	import requests as _requests

	try:
		vendor_doc = frappe.db.get_value(
			'Vendor',
			vendor,
			['webhook_url', 'webhook_secret'],
			as_dict=True
		)

		if not vendor_doc or not vendor_doc.get('webhook_url'):
			frappe.logger().warning(f"No webhook URL configured for vendor {vendor}")
			return False

		webhook_url = vendor_doc['webhook_url']
		webhook_secret = vendor_doc.get('webhook_secret') or ''

		# Build payload envelope
		envelope = {
			'event': event,
			'vendor': vendor,
			'timestamp': time.time(),
			'data': payload
		}

		body_bytes = _json.dumps(envelope, separators=(',', ':')).encode('utf-8')

		# Compute HMAC-SHA256 signature
		signature = hmac.new(
			webhook_secret.encode('utf-8'),
			body_bytes,
			hashlib.sha256
		).hexdigest()

		headers = {
			'Content-Type': 'application/json',
			'X-Webhook-Event': event,
			'X-Webhook-Signature': signature,
			'X-Webhook-Timestamp': str(int(time.time())),
		}

		response = _requests.post(
			webhook_url,
			data=body_bytes,
			headers=headers,
			timeout=10
		)
		response.raise_for_status()

		frappe.logger().info(
			f"Webhook '{event}' delivered to vendor {vendor} "
			f"(status {response.status_code})"
		)
		return True

	except Exception as exc:
		frappe.log_error(
			f"Webhook delivery failed for vendor {vendor}, event '{event}': {exc}"
		)
		return False


# ─────────────────────────────────────────────────────────────────────────────
# Frappe built-in API key/secret auth — alternative to token-based auth
# ─────────────────────────────────────────────────────────────────────────────
#
# Frappe supports API key/secret authentication natively via the User doctype
# (User > API Access section).  Vendors can authenticate server-to-server
# requests without a session token by passing:
#
#   Authorization: token <api_key>:<api_secret>
#
# Example:
#   curl -H "Authorization: token abc123:xyz789" \
#        https://erp.example.com/api/method/vendor_portal.api.vendor.get_purchase_orders
#
# To generate keys programmatically:
#
#   user = frappe.get_doc('User', 'vendor@example.com')
#   api_key = frappe.generate_hash(length=15)
#   api_secret = frappe.generate_hash(length=15)
#   user.api_key = api_key
#   user.api_secret = api_secret
#   user.save(ignore_permissions=True)
#
# This approach leverages Frappe's built-in session management and avoids
# maintaining a separate token cache.
