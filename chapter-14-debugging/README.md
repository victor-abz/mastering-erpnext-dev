# Chapter 14: Debugging Like a Pro - Tools & Techniques

## 🎯 Learning Objectives

By the end of this chapter, you will master:
- **Using Developer Mode** for effective debugging
- **Mastering bench console** for live environment introspection
- **Implementing comprehensive** error logging strategies
- **Leveraging browser DevTools** for client-side debugging
- **Understanding permission** debugging techniques

## 📚 Chapter Topics

### 14.1 Developer Mode - The Debugging Foundation

**Enabling and Configuring Developer Mode**

```python
# site_config.json - Developer mode configuration
{
    "developer_mode": 1,
    "maintenance_mode": 0,
    "disable_website_cache": 1,
    "disable_database_cache": 1,
    "auto_email_sent": 0,
    "skip_frappe_setup": 0,
    "developer": {
        "enable_jinja_debug": 1,
        "disable_js_bundling": 1,
        "disable_css_bundling": 1,
        "show_sql_queries": 1,
        "enable_profiling": 1
    }
}

# Enable via bench command
bench --site dev.local set-config developer_mode 1
bench --site dev.local set-config disable_website_cache 1
bench --site dev.local set-config disable_database_cache 1
```

**What Developer Mode Enables**

```python
# Developer mode features checklist
developer_features = {
    "debugging": {
        "show_sql_queries": "All SQL queries logged to console",
        "js_source_maps": "Unminified JavaScript with source maps",
        "template_debugging": "Jinja template error details",
        "api_responses": "Detailed API response information"
    },
    "performance": {
        "disable_caching": "No caching for immediate code changes",
        "profiling_enabled": "Performance profiling data available",
        "query_analysis": "SQL query execution times shown"
    },
    "ui_features": {
        "show_breadcrumbs": "Navigation breadcrumbs visible",
        "show_help_buttons": "Help icons and documentation links",
        "enable_desk_debug": "Additional desk debugging tools",
        "show_form_info": "Document metadata visible"
    },
    "error_handling": {
        "detailed_errors": "Full error stack traces displayed",
        "email_errors": "Errors emailed to developers",
        "error_log_access": "Real-time error log viewing"
    }
}

# Check if developer mode is enabled
def is_developer_mode():
    return frappe.conf.get("developer_mode", False)

# Conditional code based on developer mode
if is_developer_mode():
    # Development-specific code
    frappe.logger().set_level("DEBUG")
    # Enable additional logging
    # Show debug information
```

**Developer Mode Best Practices**

```python
# your_app/dev_utils.py - Developer utilities

import frappe
from frappe import _
import json
import traceback

def debug_print(message, title=None, level="INFO"):
    """Enhanced debug printing for development"""
    
    if not frappe.conf.get("developer_mode"):
        return
    
    # Format message based on type
    if isinstance(message, (dict, list)):
        formatted_message = json.dumps(message, indent=2, default=str)
    elif hasattr(message, '__dict__'):
        formatted_message = f"Object: {message.__class__.__name__}\n{json.dumps(message.__dict__, indent=2, default=str)}"
    else:
        formatted_message = str(message)
    
    # Log to file
    frappe.logger().log(level, f"{title or 'DEBUG'}: {formatted_message}")
    
    # Also print to console if running in bench console
    if hasattr(frappe.local, 'request') and frappe.local.request:
        print(f"[{level}] {title or 'DEBUG'}: {formatted_message}")

def debug_query(query, params=None, explain=False):
    """Debug SQL queries with execution details"""
    
    if not frappe.conf.get("developer_mode"):
        return
    
    try:
        start_time = frappe.utils.time.time_in_seconds()
        
        if params:
            result = frappe.db.sql(query, params, as_dict=True)
        else:
            result = frappe.db.sql(query, as_dict=True)
        
        execution_time = frappe.utils.time.time_in_seconds() - start_time
        
        debug_info = {
            "query": query,
            "params": params,
            "execution_time": f"{execution_time:.4f}s",
            "result_count": len(result) if result else 0,
            "results": result[:5] if result else []  # First 5 results
        }
        
        if explain and frappe.conf.get("show_sql_queries"):
            explain_query = f"EXPLAIN {query}"
            explain_result = frappe.db.sql(explain_query, as_dict=True)
            debug_info["explain"] = explain_result
        
        debug_print(debug_info, "SQL Query Debug")
        
        return result
        
    except Exception as e:
        debug_print({
            "error": str(e),
            "query": query,
            "params": params
        }, "SQL Query Error", "ERROR")
        raise

def debug_document(doc, show_changes=False):
    """Debug document state and changes"""
    
    if not frappe.conf.get("developer_mode"):
        return
    
    doc_info = {
        "doctype": doc.doctype,
        "name": doc.name,
        "docstatus": doc.docstatus,
        "owner": doc.owner,
        "creation": doc.creation,
        "modified": doc.modified,
        "modified_by": doc.modified_by,
        "fields": {}
    }
    
    # Get all field values
    for field in doc.meta.fields:
        fieldname = field.get("fieldname")
        if fieldname and hasattr(doc, fieldname):
            doc_info["fields"][fieldname] = doc.get(fieldname)
    
    # Show changes if document is modified
    if show_changes and hasattr(doc, '_doc_before_save'):
        changes = get_document_changes(doc)
        doc_info["changes"] = changes
    
    debug_print(doc_info, f"Document Debug: {doc.doctype} {doc.name}")

def get_document_changes(doc):
    """Get changes made to document"""
    
    if not hasattr(doc, '_doc_before_save'):
        return {}
    
    changes = {}
    old_doc = doc._doc_before_save
    
    for field in doc.meta.fields:
        fieldname = field.get("fieldname")
        if not fieldname:
            continue
        
        old_value = old_doc.get(fieldname)
        new_value = doc.get(fieldname)
        
        if old_value != new_value:
            changes[fieldname] = {
                "old": old_value,
                "new": new_value,
                "fieldtype": field.get("fieldtype")
            }
    
    return changes
```

### 14.2 Bench Console - Live Environment Introspection

**Mastering the Bench Console**

```python
# bench --site dev.local console - Essential commands

# 1. Basic document operations
>>> frappe.get_doc('Customer', 'CUST-00001')
>>> frappe.get_all('Customer', limit=5)
>>> frappe.db.count('Sales Order')

# 2. Advanced querying
>>> frappe.db.sql("SELECT * FROM `tabCustomer` WHERE customer_group = %s", ('Commercial',), as_dict=True)
>>> frappe.get_list('Sales Order', filters={'docstatus': 1}, fields=['name', 'grand_total'])

# 3. Document manipulation
>>> doc = frappe.get_doc('Customer', 'CUST-00001')
>>> doc.customer_name = 'New Name'
>>> doc.save()

# 4. Permission testing
>>> frappe.has_permission('Customer', 'write', 'CUST-00001')
>>> frappe.get_roles()
>>> frappe.get_user_permissions()

# 5. System information
>>> frappe.get_system_settings()
>>> frappe.conf.get('site_name')
>>> frappe.get_hooks()
```

**Advanced Console Techniques**

```python
# Console utility functions for debugging

def inspect_doctype(doctype):
    """Comprehensive doctype inspection"""
    
    print(f"\n=== DocType Inspection: {doctype} ===\n")
    
    # 1. Meta information
    meta = frappe.get_meta(doctype)
    print(f"Module: {meta.module}")
    print(f"Custom: {meta.custom}")
    print(f"Engine: {meta.engine}")
    
    # 2. Fields
    print(f"\n--- Fields ({len(meta.fields)}) ---")
    for field in meta.fields[:10]:  # First 10 fields
        print(f"  {field.fieldname}: {field.fieldtype} - {field.label}")
    
    if len(meta.fields) > 10:
        print(f"  ... and {len(meta.fields) - 10} more fields")
    
    # 3. Permissions
    print(f"\n--- Permissions ---")
    user_roles = frappe.get_roles()
    for role in user_roles:
        has_read = frappe.has_permission(doctype, 'read')
        has_write = frappe.has_permission(doctype, 'write')
        print(f"  {role}: Read={has_read}, Write={has_write}")
    
    # 4. Recent documents
    print(f"\n--- Recent Documents ---")
    recent_docs = frappe.get_all(doctype, 
        fields=['name', 'creation', 'owner'],
        order_by='creation desc',
        limit=5
    )
    for doc in recent_docs:
        print(f"  {doc.name}: {doc.creation} by {doc.owner}")
    
    # 5. Database table info
    print(f"\n--- Database Table ---")
    table_name = f"tab{doctype}"
    try:
        count = frappe.db.count(doctype)
        print(f"  Table: {table_name}")
        print(f"  Records: {count}")
        
        # Show table structure
        desc = frappe.db.sql(f"DESCRIBE {table_name}", as_dict=True)
        print(f"  Columns: {len(desc)}")
        
    except Exception as e:
        print(f"  Error: {str(e)}")

def debug_user_session(user=None):
    """Debug user session and permissions"""
    
    if not user:
        user = frappe.session.user
    
    print(f"\n=== User Session Debug: {user} ===\n")
    
    # 1. User information
    user_doc = frappe.get_doc('User', user)
    print(f"Name: {user_doc.full_name}")
    print(f"Email: {user_doc.email}")
    print(f"Enabled: {user_doc.enabled}")
    
    # 2. Roles
    print(f"\n--- Roles ---")
    roles = frappe.get_roles(user)
    for role in roles:
        print(f"  - {role}")
    
    # 3. User Permissions
    print(f"\n--- User Permissions ---")
    user_perms = frappe.get_user_permissions(user)
    for allow_type, values in user_perms.items():
        print(f"  {allow_type}: {list(values.keys())}")
    
    # 4. Recent activity
    print(f"\n--- Recent Activity ---")
    activity = frappe.get_all('Activity Log',
        filters={'user': user},
        fields=['operation', 'document_name', 'creation'],
        order_by='creation desc',
        limit=10
    )
    for act in activity:
        print(f"  {act.creation}: {act.operation} - {act.document_name}")

def analyze_performance(doctype, limit=10):
    """Analyze performance of a doctype"""
    
    print(f"\n=== Performance Analysis: {doctype} ===\n")
    
    # 1. Query performance
    start_time = frappe.utils.time.time_in_seconds()
    docs = frappe.get_all(doctype, limit=limit, fields=['*'])
    query_time = frappe.utils.time.time_in_seconds() - start_time
    
    print(f"Query Time (for {len(docs)} docs): {query_time:.4f}s")
    print(f"Average per doc: {(query_time/len(docs))*1000:.2f}ms")
    
    # 2. Document load time
    if docs:
        doc_name = docs[0].name
        start_time = frappe.utils.time.time_in_seconds()
        doc = frappe.get_doc(doctype, doc_name)
        load_time = frappe.utils.time.time_in_seconds() - start_time
        
        print(f"Single Document Load Time: {load_time:.4f}s")
    
    # 3. Check for indexes
    table_name = f"tab{doctype}"
    try:
        indexes = frappe.db.sql(f"SHOW INDEX FROM {table_name}", as_dict=True)
        print(f"\n--- Indexes ({len(indexes)}) ---")
        for idx in indexes[:5]:
            print(f"  {idx.Key_name}: {idx.Column_name}")
    except Exception as e:
        print(f"Error checking indexes: {str(e)}")

# Console shortcuts
def doc(doctype, name):
    """Quick document access"""
    return frappe.get_doc(doctype, name)

def all_(doctype, limit=10):
    """Quick get all"""
    return frappe.get_all(doctype, limit=limit)

def sql(query, params=None):
    """Quick SQL execution"""
    return frappe.db.sql(query, params, as_dict=True)

def perms(doctype):
    """Check permissions for doctype"""
    return {
        'read': frappe.has_permission(doctype, 'read'),
        'write': frappe.has_permission(doctype, 'write'),
        'create': frappe.has_permission(doctype, 'create'),
        'delete': frappe.has_permission(doctype, 'delete')
    }
```

### 14.3 Error Logging Best Practices

**Comprehensive Error Logging Strategy**

```python
# your_app/error_logging.py - Professional error logging

import frappe
import traceback
import sys
from datetime import datetime
from frappe.utils import now, get_url_to_report

class ErrorLogger:
    """Advanced error logging with context and categorization"""
    
    ERROR_CATEGORIES = {
        'VALIDATION': 'Data validation errors',
        'PERMISSION': 'Permission and access errors',
        'INTEGRATION': 'External API integration errors',
        'PERFORMANCE': 'Performance related issues',
        'BUSINESS_LOGIC': 'Business logic errors',
        'SYSTEM': 'System and infrastructure errors'
    }
    
    @staticmethod
    def log_error(error, category=None, context=None, reference_doc=None):
        """
        Log error with comprehensive context
        
        Args:
            error: Exception object or error message
            category: Error category from ERROR_CATEGORIES
            context: Additional context information
            reference_doc: Related document (doctype, name)
        """
        
        # Prepare error data
        error_data = ErrorLogger._prepare_error_data(error, category, context, reference_doc)
        
        # Log to Frappe error log
        frappe.log_error(
            message=error_data['message'],
            title=error_data['title'],
            reference_doctype=error_data.get('reference_doctype'),
            reference_name=error_data.get('reference_name'),
            data=error_data['context']
        )
        
        # Send notifications for critical errors
        if ErrorLogger._is_critical_error(error, category):
            ErrorLogger._send_error_notification(error_data)
        
        # Add to custom error tracking if needed
        ErrorLogger._track_error_metrics(error_data)
        
        return error_data
    
    @staticmethod
    def _prepare_error_data(error, category, context, reference_doc):
        """Prepare comprehensive error data"""
        
        # Extract error information
        if isinstance(error, Exception):
            error_message = str(error)
            error_type = error.__class__.__name__
            traceback_str = traceback.format_exc()
        else:
            error_message = str(error)
            error_type = 'Error'
            traceback_str = traceback.format_exc() if sys.exc_info()[0] else ''
        
        # Extract user and request context
        user_context = ErrorLogger._get_user_context()
        request_context = ErrorLogger._get_request_context()
        
        # Prepare base error data
        error_data = {
            'timestamp': now(),
            'error_message': error_message,
            'error_type': error_type,
            'category': category or 'SYSTEM',
            'traceback': traceback_str,
            'user': user_context,
            'request': request_context,
            'custom_context': context or {}
        }
        
        # Add document reference
        if reference_doc:
            if isinstance(reference_doc, (list, tuple)):
                error_data['reference_doctype'] = reference_doc[0]
                error_data['reference_name'] = reference_doc[1]
            else:
                error_data['reference_doctype'] = reference_doc.doctype
                error_data['reference_name'] = reference_doc.name
        
        # Create formatted message and title
        error_data['message'] = ErrorLogger._format_error_message(error_data)
        error_data['title'] = f"{error_data['category']}: {error_type}"
        error_data['context'] = error_data  # Full context for data field
        
        return error_data
    
    @staticmethod
    def _get_user_context():
        """Get user-related context"""
        
        try:
            return {
                'user': frappe.session.user,
                'roles': frappe.get_roles(),
                'user_type': frappe.db.get_value('User', frappe.session.user, 'user_type'),
                'language': frappe.session.data.get('language'),
                'timezone': frappe.session.data.get('time_zone')
            }
        except Exception:
            return {'user': 'Unknown', 'roles': [], 'user_type': 'Unknown'}
    
    @staticmethod
    def _get_request_context():
        """Get request-related context"""
        
        try:
            if hasattr(frappe.local, 'request'):
                request = frappe.local.request
                return {
                    'method': request.method,
                    'url': request.url,
                    'headers': dict(request.headers),
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', '')
                }
        except Exception:
            pass
        
        return {'method': 'Unknown', 'url': 'Unknown'}
    
    @staticmethod
    def _format_error_message(error_data):
        """Format error message for logging"""
        
        message_parts = [
            f"Error: {error_data['error_message']}",
            f"Type: {error_data['error_type']}",
            f"Category: {error_data['category']}",
            f"User: {error_data['user']['user']}",
            f"Time: {error_data['timestamp']}"
        ]
        
        # Add document reference if available
        if error_data.get('reference_doctype'):
            message_parts.append(
                f"Document: {error_data['reference_doctype']} {error_data['reference_name']}"
            )
        
        return '\n'.join(message_parts)
    
    @staticmethod
    def _is_critical_error(error, category):
        """Determine if error requires immediate notification"""
        
        critical_categories = ['SYSTEM', 'PERFORMANCE']
        critical_error_types = ['DatabaseError', 'ConnectionError', 'TimeoutError']
        
        return (
            category in critical_categories or
            any(err in str(type(error)) for err in critical_error_types) or
            'database' in str(error).lower() or
            'connection' in str(error).lower()
        )
    
    @staticmethod
    def _send_error_notification(error_data):
        """Send notification for critical errors"""
        
        try:
            # Get system administrators
            admin_users = frappe.get_all('User',
                filters={'role': 'System Manager', 'enabled': 1},
                fields=['email', 'full_name']
            )
            
            admin_emails = [user.email for user in admin_users if user.email]
            
            if admin_emails:
                # Send email notification
                frappe.sendmail(
                    recipients=admin_emails,
                    subject=f"Critical Error: {error_data['error_type']}",
                    template="critical_error_notification",
                    args=error_data,
                    reference_doctype=error_data.get('reference_doctype'),
                    reference_name=error_data.get('reference_name')
                )
                
                # Send real-time notification
                for admin_user in admin_users:
                    frappe.publish_realtime(
                        'critical_error',
                        error_data,
                        user=admin_user.email
                    )
        
        except Exception as e:
            # Don't let notification errors cause more errors
            frappe.logger().error(f"Failed to send error notification: {str(e)}")
    
    @staticmethod
    def _track_error_metrics(error_data):
        """Track error metrics for monitoring"""
        
        try:
            # Create or update error metrics
            metric_name = f"error_count_{error_data['category'].lower()}"
            
            # This would integrate with your monitoring system
            # For now, just log the metric
            frappe.logger().info(f"Error Metric: {metric_name} = 1")
            
        except Exception as e:
            frappe.logger().error(f"Failed to track error metrics: {str(e)}")

# Custom exception classes for better error handling
class BusinessLogicError(Exception):
    """Business logic validation errors"""
    def __init__(self, message, details=None, user_message=None):
        super().__init__(message)
        self.details = details or {}
        self.user_message = user_message or message

class IntegrationError(Exception):
    """External system integration errors"""
    def __init__(self, message, service=None, response=None):
        super().__init__(message)
        self.service = service
        self.response = response

class ValidationError(Exception):
    """Data validation errors"""
    def __init__(self, message, field=None, value=None):
        super().__init__(message)
        self.field = field
        self.value = value

# Decorator for automatic error logging
def log_errors(category='BUSINESS_LOGIC', return_on_error=None):
    """Decorator to automatically log function errors"""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the error with context
                ErrorLogger.log_error(
                    error=e,
                    category=category,
                    context={
                        'function': func.__name__,
                        'module': func.__module__,
                        'args': str(args)[:200],  # Limit length
                        'kwargs': str(kwargs)[:200]
                    }
                )
                
                # Return default value if specified
                if return_on_error is not None:
                    return return_on_error
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator

# Usage examples
@log_errors(category='INTEGRATION', return_on_error={'status': 'error'})
def call_external_api(api_url, data):
    """Example function with automatic error logging"""
    
    import requests
    
    response = requests.post(api_url, json=data)
    response.raise_for_status()
    
    return response.json()
```

### 14.4 Browser DevTools for Client-Side Debugging

**Mastering Chrome DevTools for Frappe Development**

```javascript
// public/js/debug_tools.js - Client-side debugging utilities

// 1. Enhanced Console Logging
window.FrappeDebug = {
    // Enhanced logging with context
    log: function(message, data, level = 'info') {
        const timestamp = new Date().toISOString();
        const user = frappe.session.user;
        
        console.group(`[${level.toUpperCase()}] ${timestamp} - ${user}`);
        console.log(message);
        
        if (data) {
            if (typeof data === 'object') {
                console.table ? console.table(data) : console.dir(data);
            } else {
                console.log(data);
            }
        }
        
        console.groupEnd();
        
        // Also send to server for centralized logging
        this.logToServer(message, data, level);
    },
    
    // Send client logs to server
    logToServer: function(message, data, level) {
        frappe.call({
            method: 'your_app.debug.log_client_message',
            args: {
                message: message,
                data: JSON.stringify(data),
                level: level,
                page: window.location.pathname,
                user_agent: navigator.userAgent
            },
            callback: function(r) {
                // Handle response if needed
            }
        });
    },
    
    // Document debugging
    inspectDocument: function(doctype, name) {
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: doctype,
                name: name
            },
            callback: function(r) {
                if (r.docs && r.docs.length > 0) {
                    const doc = r.docs[0];
                    console.group(`Document Inspection: ${doctype} ${name}`);
                    console.log('Document:', doc);
                    console.log('Meta:', frappe.meta.docinfo[doctype]);
                    console.log('Permissions:', frappe.perm);
                    console.groupEnd();
                }
            }
        });
    },
    
    // Form debugging
    inspectForm: function() {
        if (!cur_frm) {
            console.error('No current form found');
            return;
        }
        
        const frm = cur_frm;
        console.group(`Form Inspection: ${frm.doctype} ${frm.docname}`);
        
        // Form information
        console.log('Form Object:', frm);
        console.log('Document:', frm.doc);
        console.log('Meta:', frm.meta);
        
        // Fields information
        const fields = {};
        Object.keys(frm.fields_dict).forEach(function(fieldname) {
            const field = frm.fields_dict[fieldname];
            fields[fieldname] = {
                type: field.df.fieldtype,
                value: field.get_value(),
                label: field.df.label,
                hidden: field.df.hidden,
                read_only: field.df.read_only
            };
        });
        console.table(fields);
        
        // Permissions
        console.log('Permissions:', {
            read: frm.perm.read,
            write: frm.perm.write,
            create: frm.perm.create,
            delete: frm.perm.delete,
            submit: frm.perm.submit,
            cancel: frm.perm.cancel
        });
        
        console.groupEnd();
    },
    
    // API call debugging
    debugAPICall: function(method, args = {}) {
        const startTime = performance.now();
        
        console.group(`API Call: ${method}`);
        console.log('Arguments:', args);
        
        frappe.call({
            method: method,
            args: args,
            callback: function(r) {
                const endTime = performance.now();
                const duration = endTime - startTime;
                
                console.log('Response:', r);
                console.log(`Duration: ${duration.toFixed(2)}ms`);
                console.groupEnd();
                
                // Log performance metrics
                if (duration > 1000) {
                    FrappeDebug.log(`Slow API call detected: ${method}`, {
                        duration: duration,
                        args: args
                    }, 'warn');
                }
            },
            error: function(r) {
                const endTime = performance.now();
                const duration = endTime - startTime;
                
                console.error('API Error:', r);
                console.log(`Duration: ${duration.toFixed(2)}ms`);
                console.groupEnd();
                
                FrappeDebug.log(`API call failed: ${method}`, {
                    error: r,
                    duration: duration,
                    args: args
                }, 'error');
            }
        });
    },
    
    // Performance monitoring
    monitorPerformance: function() {
        if (window.performance && window.performance.timing) {
            const timing = window.performance.timing;
            const loadTime = timing.loadEventEnd - timing.navigationStart;
            const domReady = timing.domContentLoadedEventEnd - timing.navigationStart;
            
            console.group('Performance Metrics');
            console.log('Total Load Time:', loadTime + 'ms');
            console.log('DOM Ready Time:', domReady + 'ms');
            console.log('Network Time:', timing.responseEnd - timing.requestStart + 'ms');
            
            // Resource timing
            const resources = performance.getEntriesByType('resource');
            const slowResources = resources.filter(r => r.duration > 1000);
            
            if (slowResources.length > 0) {
                console.warn('Slow Resources:', slowResources);
            }
            
            console.groupEnd();
        }
    },
    
    // Memory usage
    checkMemory: function() {
        if (window.performance && window.performance.memory) {
            const memory = window.performance.memory;
            
            console.group('Memory Usage');
            console.log('Used:', Math.round(memory.usedJSHeapSize / 1048576) + ' MB');
            console.log('Total:', Math.round(memory.totalJSHeapSize / 1048576) + ' MB');
            console.log('Limit:', Math.round(memory.jsHeapSizeLimit / 1048576) + ' MB');
            console.groupEnd();
        }
    },
    
    // Network debugging
    monitorNetwork: function() {
        // Monitor failed requests
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            return originalFetch.apply(this, args)
                .then(response => {
                    if (!response.ok) {
                        FrappeDebug.log('Network request failed', {
                            url: args[0],
                            status: response.status,
                            statusText: response.statusText
                        }, 'error');
                    }
                    return response;
                })
                .catch(error => {
                    FrappeDebug.log('Network request error', {
                        url: args[0],
                        error: error.message
                    }, 'error');
                    throw error;
                });
        };
    }
};

// Auto-initialize debugging tools
$(document).ready(function() {
    // Add debugging shortcuts
    window.debugForm = FrappeDebug.inspectForm;
    window.debugDoc = FrappeDebug.inspectDocument;
    window.debugAPI = FrappeDebug.debugAPICall;
    window.debugPerf = FrappeDebug.monitorPerformance;
    window.debugMem = FrappeDebug.checkMemory;
    
    // Monitor performance on page load
    setTimeout(FrappeDebug.monitorPerformance, 1000);
    
    // Check memory usage periodically
    setInterval(FrappeDebug.checkMemory, 30000); // Every 30 seconds
    
    // Initialize network monitoring
    FrappeDebug.monitorNetwork();
    
    console.log('Frappe Debug Tools initialized. Available commands:');
    console.log('- debugForm() - Inspect current form');
    console.log('- debugDoc(doctype, name) - Inspect document');
    console.log('- debugAPI(method, args) - Debug API call');
    console.log('- debugPerf() - Show performance metrics');
    console.log('- debugMem() - Check memory usage');
});
```

### 14.5 Permission Debugging

**Debugging Permission Issues**

```python
# your_app/permission_debug.py - Permission debugging tools

import frappe
from frappe.permissions import get_user_permissions, get_role_permissions

class PermissionDebugger:
    """Comprehensive permission debugging utilities"""
    
    @staticmethod
    def debug_document_permission(doctype, name, user=None):
        """Debug why user has/doesn't have permission to document"""
        
        if not user:
            user = frappe.session.user
        
        print(f"\n=== Permission Debug: {user} on {doctype} {name} ===\n")
        
        # 1. Basic permission check
        permissions = ['read', 'write', 'create', 'delete', 'submit', 'cancel', 'amend']
        
        print("--- Basic Permissions ---")
        for perm in permissions:
            has_perm = frappe.has_permission(doctype, perm, name, user)
            print(f"{perm}: {'✓' if has_perm else '✗'}")
        
        # 2. Role analysis
        print(f"\n--- Role Analysis ---")
        user_roles = frappe.get_roles(user)
        print(f"User Roles: {', '.join(user_roles)}")
        
        # Check role permissions for this doctype
        for role in user_roles:
            role_perms = get_role_permissions(role, doctype)
            if role_perms:
                print(f"\n{role}:")
                for perm in permissions:
                    has_role_perm = role_perms.get(perm, 0)
                    print(f"  {perm}: {'✓' if has_role_perm else '✗'}")
        
        # 3. Document ownership
        print(f"\n--- Document Ownership ---")
        try:
            doc = frappe.get_doc(doctype, name)
            print(f"Document Owner: {doc.owner}")
            print(f"Is Owner: {doc.owner == user}")
            print(f"DocStatus: {doc.docstatus}")
            
            # Check if_owner permissions
            if hasattr(doc, 'if_owner'):
                print(f"If Owner Permission: {doc.if_owner}")
        except Exception as e:
            print(f"Error loading document: {str(e)}")
        
        # 4. User permissions (row-level)
        print(f"\n--- User Permissions (Row-Level) ---")
        user_perms = get_user_permissions(user)
        
        # Check relevant user permissions for this doctype
        relevant_perms = {}
        for allow_type, perm_data in user_perms.items():
            if allow_type.lower() in [doctype.lower(), 'customer', 'supplier', 'project']:
                relevant_perms[allow_type] = perm_data
        
        if relevant_perms:
            for allow_type, perm_data in relevant_perms.items():
                print(f"{allow_type}: {list(perm_data.keys())}")
        else:
            print("No relevant user permissions found")
        
        # 5. Permission query conditions
        print(f"\n--- Permission Query Conditions ---")
        if doctype in frappe.permission_query_conditions:
            condition_func = frappe.permission_query_conditions[doctype]
            try:
                match_condition = condition_func(user)
                print(f"Match Condition: {match_condition}")
                
                # Test the condition
                test_query = f"""
                    SELECT COUNT(*) as count 
                    FROM `tab{doctype}` 
                    WHERE name = %s AND ({match_condition})
                """
                result = frappe.db.sql(test_query, (name,), as_dict=True)
                print(f"Condition Test: {'✓' if result[0].count > 0 else '✗'}")
                
            except Exception as e:
                print(f"Error in match condition: {str(e)}")
        else:
            print("No custom permission query conditions")
        
        # 6. Property setters affecting permissions
        print(f"\n--- Property Setters ---")
        property_setters = frappe.get_all('Property Setter',
            filters={
                'doc_type': doctype,
                'property': ['in', ['read_only', 'hidden', 'permlevel']]
            },
            fields=['property', 'value', 'field_name']
        )
        
        if property_setters:
            for ps in property_setters:
                print(f"{ps.property} on {ps.field_name or 'Document'}: {ps.value}")
        else:
            print("No permission-affecting property setters")
        
        # 7. Custom DocPerm analysis
        print(f"\n--- Custom DocPerm Analysis ---")
        custom_perms = frappe.get_all('Custom DocPerm',
            filters={'parent': doctype},
            fields=['role', 'read', 'write', 'create', 'delete', 'submit', 'cancel', 'if_owner', 'permlevel']
        )
        
        if custom_perms:
            print(f"Found {len(custom_perms)} custom permission rules:")
            for perm in custom_perms:
                if perm.role in user_roles:
                    print(f"  {perm.role} (Level {perm.permlevel}):")
                    for p in ['read', 'write', 'create', 'delete', 'submit', 'cancel']:
                        if getattr(perm, p, 0):
                            print(f"    {p}: ✓")
                    if perm.if_owner:
                        print(f"    if_owner: ✓")
        else:
            print("No custom DocPerm rules found")
    
    @staticmethod
    def debug_role_permission(role, doctype):
        """Debug role permissions for a specific doctype"""
        
        print(f"\n=== Role Permission Debug: {role} on {doctype} ===\n")
        
        # Get role permissions
        role_perms = get_role_permissions(role, doctype)
        
        if role_perms:
            print("Role Permissions:")
            for perm, value in role_perms.items():
                print(f"  {perm}: {'✓' if value else '✗'}")
        else:
            print("No specific permissions for this role")
        
        # Check if role exists
        role_doc = frappe.db.exists('Role', role)
        if role_doc:
            print(f"\nRole exists: ✓")
            role_info = frappe.get_doc('Role', role)
            print(f"Desk Access: {role_info.desk_access}")
            print(f"Restrict to Domain: {role_info.restrict_to_domain}")
        else:
            print(f"\nRole exists: ✗")
    
    @staticmethod
    def debug_user_permissions(user=None):
        """Debug all user permissions"""
        
        if not user:
            user = frappe.session.user
        
        print(f"\n=== User Permissions Debug: {user} ===\n")
        
        user_perms = get_user_permissions(user)
        
        if user_perms:
            print(f"Found {len(user_perms)} permission types:")
            
            for allow_type, perm_data in user_perms.items():
                print(f"\n{allow_type}:")
                for value, doctypes in perm_data.items():
                    print(f"  {value}: {', '.join(doctypes)}")
        else:
            print("No user permissions found")
    
    @staticmethod
    def debug_permission_cache(doctype, user=None):
        """Debug permission cache status"""
        
        if not user:
            user = frappe.session.user
        
        print(f"\n=== Permission Cache Debug: {user} on {doctype} ===\n")
        
        # Check cache keys
        cache_keys = [
            f'perm:{user}:{doctype}',
            f'perm_query_conditions:{user}:{doctype}',
            f'user_permissions:{user}'
        ]
        
        for key in cache_keys:
            cached_value = frappe.cache().get_value(key)
            if cached_value:
                print(f"{key}: ✓ (Cached)")
                if len(str(cached_value)) < 500:
                    print(f"  Value: {cached_value}")
                else:
                    print(f"  Value: ({len(str(cached_value))} characters)")
            else:
                print(f"{key}: ✗ (Not cached)")
    
    @staticmethod
    def clear_permission_cache(user=None):
        """Clear permission cache for debugging"""
        
        if not user:
            user = frappe.session.user
        
        # Clear all permission-related cache
        cache_patterns = [
            f'perm:{user}:*',
            f'perm_query_conditions:{user}:*',
            f'user_permissions:{user}'
        ]
        
        for pattern in cache_patterns:
            keys = frappe.cache().get_keys(pattern)
            for key in keys:
                frappe.cache().delete_value(key)
        
        print(f"Permission cache cleared for user: {user}")

# Console shortcuts for permission debugging
def debug_perm(doctype, name=None, user=None):
    """Quick permission debug"""
    if name:
        PermissionDebugger.debug_document_permission(doctype, name, user)
    else:
        PermissionDebugger.debug_user_permissions(user)

def debug_role(role, doctype):
    """Quick role permission debug"""
    PermissionDebugger.debug_role_permission(role, doctype)

def clear_perm_cache(user=None):
    """Clear permission cache"""
    PermissionDebugger.clear_permission_cache(user)
```

## 🛠️ Practical Exercises

### Exercise 14.1: Developer Mode Deep Dive

1. Enable developer mode and explore all features
2. Create a custom debug utility function
3. Test SQL query debugging with explain plans
4. Analyze performance impact of developer mode

### Exercise 14.2: Console Mastery

1. Create custom console shortcuts for common tasks
2. Build a permission debugging console tool
3. Implement document inspection utilities
4. Create performance analysis functions

### Exercise 14.3: Error Logging System

1. Implement comprehensive error logging
2. Create error categorization and notification
3. Build error tracking and metrics
4. Test error handling in different scenarios

## 🤔 Thought Questions

1. How do you balance debugging features with production performance?
2. What are the security implications of detailed error logging?
3. How do you debug intermittent issues that are hard to reproduce?
4. What tools and techniques work best for client-side vs server-side debugging?

## 📖 Further Reading

- [Frappe Developer Mode Guide](https://frappeframework.com/docs/user/en/developer-mode)
- [Chrome DevTools Documentation](https://developer.chrome.com/docs/devtools)
- [Python Logging Best Practices](https://docs.python.org/3/library/logging.html)

## 🎯 Chapter Summary

Professional debugging requires a systematic approach:

- **Developer Mode** provides comprehensive debugging features
- **Bench Console** enables live environment introspection
- **Error Logging** captures issues with full context
- **Browser DevTools** essential for client-side debugging
- **Permission Debugging** resolves access control issues
- **Performance Monitoring** identifies optimization opportunities

---

**Next Chapter**: Building automated testing strategies.


---

## Addendum: pdb/ipdb Integration & Logger Guidance

### A.1 Using `pdb` / `ipdb` with Bench

Standard Python debuggers work inside Frappe's worker processes. The key is to attach to the **foreground** bench process, not a daemonised supervisor worker.

**Step 1 — run bench in the foreground**

```bash
# Terminal 1: start bench without supervisor so stdout is visible
bench serve --port 8000
# or for background workers:
bench worker --queue default
```

**Step 2 — insert a breakpoint in your code**

```python
# your_app/doctype/asset/asset.py
def validate(self):
    # Standard library — no extra install needed (Python 3.7+)
    breakpoint()          # equivalent to import pdb; pdb.set_trace()
    self._check_purchase_cost()
```

For a richer REPL (syntax highlighting, tab completion) install `ipdb`:

```bash
pip install ipdb
```

```python
import ipdb; ipdb.set_trace()
```

**Step 3 — trigger the code path** (save the document, call the API, etc.) and the debugger prompt appears in Terminal 1.

Common pdb commands:

| Command | Action |
|---------|--------|
| `n` | next line (step over) |
| `s` | step into function |
| `c` | continue execution |
| `p expr` | print expression |
| `pp expr` | pretty-print expression |
| `l` | list surrounding source |
| `bt` | print call stack |
| `q` | quit debugger |

> **Note:** Never leave `breakpoint()` calls in committed code. Use a pre-commit hook or `grep -r "breakpoint()" apps/` in CI to catch them.

### A.2 `frappe.logger()` vs `frappe.log_error()` — When to Use Which

| | `frappe.logger()` | `frappe.log_error()` |
|---|---|---|
| **What it does** | Returns a Python `logging.Logger` instance; writes to `logs/<site>.log` | Creates an **Error Log** document in the database and optionally emails admins |
| **Severity levels** | DEBUG, INFO, WARNING, ERROR, CRITICAL | Always stored as an error; no severity levels |
| **Visible in UI** | No (file only) | Yes — Desk → Error Log list |
| **Performance** | Very low overhead | Writes a DB row; avoid in hot paths |
| **Best for** | Diagnostic traces, INFO/DEBUG messages, performance timings | Unexpected exceptions that need human review |
| **Retention** | Rotated by `logrotate` / bench log rotation | Stays in DB until manually cleared |

```python
import frappe

# --- Use frappe.logger() for routine diagnostics ---
logger = frappe.logger("asset_management", allow_site=True, file_count=50)

def sync_assets():
    logger.info("Starting asset sync")
    try:
        count = _do_sync()
        logger.info("Sync complete: %d assets processed", count)
    except Exception:
        # Log full traceback to file at ERROR level
        logger.exception("Asset sync failed")
        raise

# --- Use frappe.log_error() for exceptions that need a ticket ---
def submit_asset(asset_name: str):
    try:
        doc = frappe.get_doc("Asset", asset_name)
        doc.submit()
    except Exception as exc:
        # Creates an Error Log row visible in the Desk
        frappe.log_error(
            title=f"Failed to submit Asset {asset_name}",
            message=frappe.get_traceback(),
            reference_doctype="Asset",
            reference_name=asset_name,
        )
        frappe.throw(f"Could not submit asset: {exc}")
```

Rule of thumb: use `frappe.logger()` for everything you would normally `print()` during development, and `frappe.log_error()` only when you need the error to surface in the Desk for an admin to act on.
