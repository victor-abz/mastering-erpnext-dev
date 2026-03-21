# -*- coding: utf-8 -*-
"""
System Health Check Script
Chapter 17: Production Pipeline
"""

import frappe
from frappe.utils import now, get_datetime
import shutil
import os
import json

@frappe.whitelist(allow_guest=True)
def health_check():
	"""Basic health check endpoint"""
	return {
		'status': 'healthy',
		'timestamp': now(),
		'version': frappe.__version__
	}

@frappe.whitelist()
def detailed_health_check():
	"""Detailed system health check"""
	return {
		'database': check_database_health(),
		'redis': check_redis_health(),
		'workers': check_worker_health(),
		'disk': check_disk_usage(),
		'memory': check_memory_usage(),
		'scheduler': check_scheduler_health()
	}

def check_database_health():
	"""Check database connectivity and performance"""
	try:
		start_time = get_datetime()
		frappe.db.sql("SELECT 1")
		response_time = (get_datetime() - start_time).total_seconds()
		
		return {
			'status': 'healthy',
			'response_time': response_time,
			'connections': get_db_connections()
		}
	except Exception as e:
		return {
			'status': 'unhealthy',
			'error': str(e)
		}

def get_db_connections():
	"""Get database connection count"""
	try:
		result = frappe.db.sql("SHOW STATUS LIKE 'Threads_connected'", as_dict=True)
		return int(result[0].Value) if result else 0
	except:
		return 0

def check_redis_health():
	"""Check Redis connectivity"""
	try:
		frappe.cache().ping()
		return {'status': 'healthy'}
	except Exception as e:
		return {'status': 'unhealthy', 'error': str(e)}

def check_worker_health():
	"""Check background worker status"""
	try:
		workers = frappe.get_all('RQ Worker',
			fields=['name', 'status', 'last_seen']
		)
		
		active_workers = [w for w in workers if w.status == 'Active']
		
		return {
			'status': 'healthy' if active_workers else 'warning',
			'total_workers': len(workers),
			'active_workers': len(active_workers)
		}
	except Exception as e:
		return {'status': 'unknown', 'error': str(e)}

def check_disk_usage():
	"""Check disk usage"""
	try:
		total, used, free = shutil.disk_usage('/')
		percent = round(used / total * 100, 1)

		return {
			'status': 'healthy' if percent < 80 else 'warning',
			'total_gb': round(total / (1024**3), 2),
			'used_gb': round(used / (1024**3), 2),
			'free_gb': round(free / (1024**3), 2),
			'percent_used': percent
		}
	except Exception as e:
		return {'status': 'unknown', 'error': str(e)}

def check_memory_usage():
	"""Check memory usage (reads /proc/meminfo on Linux)"""
	try:
		meminfo = {}
		with open('/proc/meminfo') as f:
			for line in f:
				key, val = line.split(':')
				meminfo[key.strip()] = int(val.split()[0]) * 1024  # kB -> bytes

		total = meminfo.get('MemTotal', 0)
		available = meminfo.get('MemAvailable', 0)
		used = total - available
		percent = round(used / total * 100, 1) if total else 0

		return {
			'status': 'healthy' if percent < 80 else 'warning',
			'total_gb': round(total / (1024**3), 2),
			'used_gb': round(used / (1024**3), 2),
			'available_gb': round(available / (1024**3), 2),
			'percent_used': percent
		}
	except Exception as e:
		return {'status': 'unknown', 'error': str(e)}

def check_scheduler_health():
	"""Check scheduler status"""
	try:
		scheduler_status = frappe.db.get_single_value('System Settings', 'enable_scheduler')
		
		return {
			'status': 'healthy' if scheduler_status else 'disabled',
			'enabled': scheduler_status
		}
	except Exception as e:
		return {'status': 'unknown', 'error': str(e)}
