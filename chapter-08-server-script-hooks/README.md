# Chapter 8: Server Script Hooks & Schedulers - Automation Engine

## 🎯 Learning Objectives

By the end of this chapter, you will master:
- **How to use** `hooks.py` for cross-application event handling
- **Building robust** scheduled jobs with error handling
- **Managing background** jobs and long-running tasks
- **Monitoring** job queues and worker processes
- **Implementing** email queues and notification patterns

## 📚 Chapter Topics

### 8.1 `hooks.py` Deep Dive - The Event System

**Understanding Hook Categories**

```python
# In your_app/hooks.py - Complete hook reference

# ==============
# Document Events
# ==============
doc_events = {
    "Sales Order": {
        "on_update": "your_app.events.sales_order_on_update",
        "on_submit": "your_app.events.sales_order_on_submit", 
        "on_cancel": "your_app.events.sales_order_on_cancel",
        "before_submit": "your_app.events.validate_sales_order",
        "on_trash": "your_app.events.sales_order_on_trash"
    },
    "Customer": {
        "validate": "your_app.events.validate_customer_credit_limit"
    }
}

# =================
# Scheduler Events  
# =================
scheduler_events = {
    "daily": [
        "your_app.scripts.daily_send_expiry_notifications",
        "your_app.scripts.daily_generate_reports"
    ],
    "weekly": [
        "your_app.scripts.weekly_backup_database"
    ],
    "monthly": [
        "your_app.scripts.monthly_archive_old_records"
    ],
    "hourly": [
        "your_app.scripts.hourly_sync_external_data"
    ]
}

# ==============
# App Hooks
# ==============
app_include_js = "/assets/your_app/js/custom.js"
app_include_css = "/assets/your_app/css/custom.css"

# ==============
# Permission Hooks
# ==============
permission_query_conditions = {
    "Sales Order": "your_app.permissions.get_sales_order_conditions",
    "Customer": "your_app.permissions.get_customer_conditions"
}

# ==============
# Data Migration Hooks
# ==============
fixtures = [
    {"dt": "Custom Field", "filters": [{"fieldname": "like", "value": "custom_%"}]},
    {"dt": "Role", "filters": [{"name": "in", "value": ["Custom Manager", "Custom User"]}]}
]

# ==============
# API Whitelist Hooks
# ==============
whitelisted_methods = [
    "your_app.api.get_custom_data",
    "your_app.api.process_external_request"
]

# ==============
# UI Hooks
# ==============
doctype_js = {
    "Sales Order": "your_app/public/js/sales_order.js"
}

doctype_css = {
    "Sales Order": "your_app/public/css/sales_order.css"
}
```

**Document Events Execution Order**

```python
# Complete document lifecycle with hooks
class Document:
    def insert(self):
        # 1. before_insert hooks
        run_hook("before_insert", self)
        
        # 2. validate hooks  
        self.validate()
        run_hook("validate", self)
        
        # 3. Database insertion
        self.db_insert()
        
        # 4. after_insert hooks
        run_hook("after_insert", self)
        
        # 5. on_update hooks
        run_hook("on_update", self)
    
    def submit(self):
        # 1. before_submit hooks
        run_hook("before_submit", self)
        
        # 2. Additional validation
        self.validate_submit()
        
        # 3. Database update (docstatus = 1)
        self.db_update()
        
        # 4. on_submit hooks
        run_hook("on_submit", self)
        
        # 5. on_update hooks
        run_hook("on_update", self)
```

**Best Practices for Hook Functions**

```python
# your_app/events.py - Professional hook implementations

import frappe
from frappe import _

def sales_order_on_submit(doc, method):
    """
    Executed when Sales Order is submitted
    - Creates Project if required
    - Sends notification to team
    - Updates customer statistics
    """
    try:
        # 1. Create Project if project_type is specified
        if doc.project_type and not doc.project:
            create_project_from_sales_order(doc)
        
        # 2. Send notification to sales team
        send_sales_order_notification(doc)
        
        # 3. Update customer statistics
        update_customer_order_stats(doc)
        
        frappe.logger().info(f"Sales Order {doc.name} processed successfully")
        
    except Exception as e:
        # Log error but don't fail submission
        frappe.log_error(
            message=f"Error in sales_order_on_submit: {str(e)}",
            title=f"Sales Order {doc.name} Hook Error"
        )
        # Optionally show message to user
        frappe.msgprint(
            _("Some automated actions failed. Please check error logs."),
            indicator="warning"
        )

def create_project_from_sales_order(doc):
    """Create a project linked to sales order"""
    project = frappe.get_doc({
        "doctype": "Project",
        "project_name": f"{doc.name} - {doc.customer}",
        "customer": doc.customer,
        "sales_order": doc.name,
        "expected_start_date": doc.transaction_date,
        "expected_end_date": doc.delivery_date
    })
    project.insert()
    
    # Link back to sales order
    doc.project = project.name
    doc.db_update()

def send_sales_order_notification(doc):
    """Send notification to relevant team members"""
    # Get sales team email addresses
    recipients = []
    for team_member in doc.get("sales_team"):
        if team_member.email:
            recipients.append(team_member.email)
    
    if recipients:
        frappe.sendmail(
            recipients=recipients,
            subject=f"New Sales Order: {doc.name}",
            template="sales_order_notification",
            args=dict(
                sales_order=doc.name,
                customer=doc.customer_name,
                amount=doc.grand_total
            ),
            reference_doctype=doc.doctype,
            reference_name=doc.name
        )
```

### 8.2 Scheduled Events - Time-Based Automation

**Understanding Scheduler Patterns**

```python
# your_app/schedulers.py - Comprehensive scheduling examples

import frappe
from datetime import datetime, timedelta
from frappe.utils import nowdate, add_to_date, getdate

@frappe.whitelist()
def daily_send_expiry_notifications():
    """
    Daily job: Send notifications for documents expiring soon
    Runs every day at 2:00 AM
    """
    try:
        # 1. Find contracts expiring in next 30 days
        expiring_contracts = frappe.get_all("Contract",
            filters={
                "end_date": ["between", [nowdate(), add_to_date(nowdate(), days=30)]],
                "status": "Active"
            },
            fields=["name", "contract_name", "customer", "end_date"]
        )
        
        # 2. Group by customer for batch notifications
        customer_contracts = {}
        for contract in expiring_contracts:
            customer = contract.customer
            if customer not in customer_contracts:
                customer_contracts[customer] = []
            customer_contracts[customer].append(contract)
        
        # 3. Send notifications
        for customer, contracts in customer_contracts.items():
            send_contract_expiry_notification(customer, contracts)
        
        frappe.logger().info(f"Sent {len(expiring_contracts)} contract expiry notifications")
        
    except Exception as e:
        frappe.log_error(f"Daily expiry notifications failed: {str(e)}")

def send_contract_expiry_notification(customer, contracts):
    """Send contract expiry notification to customer"""
    try:
        # Get customer email
        customer_email = frappe.db.get_value("Customer", customer, "email_id")
        if not customer_email:
            frappe.logger().warning(f"No email found for customer {customer}")
            return
        
        # Prepare email content
        email_context = {
            "customer_name": frappe.db.get_value("Customer", customer, "customer_name"),
            "contracts": contracts,
            "total_contracts": len(contracts)
        }
        
        # Send email
        frappe.sendmail(
            recipients=[customer_email],
            subject="Important: Your Contracts Are Expiring Soon",
            template="contract_expiry_notification",
            args=email_context,
            reference_doctype="Customer",
            reference_name=customer
        )
        
        frappe.logger().info(f"Sent expiry notification to {customer}")
        
    except Exception as e:
        frappe.log_error(f"Failed to send notification to {customer}: {str(e)}")
        # Continue with other customers even if one fails

@frappe.whitelist()
def weekly_generate_performance_reports():
    """
    Weekly job: Generate and email performance reports
    Runs every Monday at 6:00 AM
    """
    try:
        # 1. Generate sales performance report
        sales_report = generate_sales_performance_report()
        
        # 2. Generate project progress report  
        project_report = generate_project_progress_report()
        
        # 3. Email to management
        management_recipients = get_management_email_list()
        
        frappe.sendmail(
            recipients=management_recipients,
            subject="Weekly Performance Reports",
            template="weekly_performance_reports",
            args=dict(
                sales_report=sales_report,
                project_report=project_report,
                report_date=getdate()
            )
        )
        
        frappe.logger().info("Weekly performance reports generated and sent")
        
    except Exception as e:
        frappe.log_error(f"Weekly report generation failed: {str(e)}")

@frappe.whitelist()
def monthly_archive_old_records():
    """
    Monthly job: Archive old records to improve performance
    Runs on 1st of every month at 3:00 AM
    """
    try:
        # Archive completed orders older than 2 years
        archive_date = add_to_date(nowdate(), years=-2)
        
        old_orders = frappe.get_all("Sales Order",
            filters={
                "docstatus": 2,  # Cancelled
                "creation": ["<", archive_date]
            }
        )
        
        for order in old_orders:
            archive_document("Sales Order", order.name)
        
        frappe.logger().info(f"Archived {len(old_orders)} old sales orders")
        
    except Exception as e:
        frappe.log_error(f"Monthly archival failed: {str(e)}")
```

**Advanced Scheduling with Cron Patterns**

```python
# Custom cron-like scheduling using frappe.utils.cron
from frappe.utils import cint, now_datetime

@frappe.whitelist()
def hourly_sync_external_data():
    """
    Hourly job: Sync data from external APIs
    Runs every hour at minute 15
    """
    # Only run at 15 minutes past the hour
    if now_datetime().minute != 15:
        return
    
    try:
        # Sync from multiple external systems
        sync_crm_data()
        sync_inventory_data()
        sync_accounting_data()
        
        frappe.logger().info("Hourly external data sync completed")
        
    except Exception as e:
        frappe.log_error(f"Hourly sync failed: {str(e)}")

def sync_crm_data():
    """Sync customer data from external CRM"""
    # Implementation for CRM API integration
    pass

def sync_inventory_data():
    """Sync inventory levels from warehouse system"""
    # Implementation for warehouse API integration  
    pass

def sync_accounting_data():
    """Sync accounting data from external system"""
    # Implementation for accounting API integration
    pass
```

### 8.3 Background Jobs - Long-Running Tasks

**Understanding Background Job Architecture**

```python
# your_app/background_jobs.py - Background job management

import frappe
from frappe.utils.background_jobs import enqueue
import time

@frappe.whitelist()
def generate_complex_report(doctype, filters, report_name):
    """
    Long-running report generation - runs in background
    """
    try:
        # 1. Create report record
        report_doc = frappe.get_doc({
            "doctype": "Custom Report",
            "name": report_name,
            "status": "Queued",
            "progress": 0
        })
        report_doc.insert()
        
        # 2. Process in chunks for large datasets
        total_records = frappe.db.count(doctype, filters)
        chunk_size = 1000
        processed = 0
        
        report_data = []
        
        for offset in range(0, total_records, chunk_size):
            # Get chunk of data
            chunk = frappe.get_all(doctype,
                filters=filters,
                fields=["*"],
                start=offset,
                limit=chunk_size
            )
            
            # Process chunk
            processed_chunk = process_report_chunk(chunk)
            report_data.extend(processed_chunk)
            
            # Update progress
            processed = min(offset + chunk_size, total_records)
            progress = (processed / total_records) * 100
            
            report_doc.progress = progress
            report_doc.db_update()
            
            # Allow other jobs to run
            frappe.db.commit()
            time.sleep(0.1)  # Prevent CPU overload
        
        # 3. Finalize report
        report_doc.status = "Completed"
        report_doc.progress = 100
        report_doc.result_data = report_data
        report_doc.db_update()
        
        # 4. Notify completion
        frappe.publish_realtime(
            "report_completed",
            {"report_name": report_name},
            user=frappe.session.user
        )
        
    except Exception as e:
        # Handle errors
        report_doc.status = "Failed"
        report_doc.error_message = str(e)
        report_doc.db_update()
        
        frappe.log_error(f"Report generation failed: {str(e)}")

# How to enqueue the job
def enqueue_report_generation(doctype, filters, report_name):
    """Queue the report generation job"""
    enqueue(
        "your_app.background_jobs.generate_complex_report",
        doctype=doctype,
        filters=filters,
        report_name=report_name,
        queue="long",  # Use long-running queue
        timeout=3600,   # 1 hour timeout
        now=True        # Start immediately
    )
```

**Managing Job Queues**

```python
# your_app/job_management.py - Job queue monitoring and control

import frappe
from frappe.utils.background_jobs import get_jobs

def get_job_status(job_id):
    """Get status of a specific background job"""
    jobs = get_jobs()
    
    for queue_name, queue_jobs in jobs.items():
        if job_id in queue_jobs:
            return {
                "job_id": job_id,
                "queue": queue_name,
                "status": "Running"
            }
    
    # Check if completed (in job history)
    job_history = frappe.get_all("Background Job History",
        filters={"job_id": job_id},
        fields=["status", "creation", "modified"]
    )
    
    if job_history:
        return {
            "job_id": job_id,
            "status": job_history[0].status,
            "creation": job_history[0].creation,
            "modified": job_history[0].modified
        }
    
    return {"job_id": job_id, "status": "Not Found"}

def cancel_job(job_id):
    """Cancel a running background job"""
    try:
        # Frappe doesn't have direct job cancellation
        # This is a workaround using job status tracking
        frappe.db.set_value("Background Job History", job_id, "status", "Cancelled")
        frappe.db.commit()
        return True
    except Exception as e:
        frappe.log_error(f"Failed to cancel job {job_id}: {str(e)}")
        return False

def retry_failed_job(job_id):
    """Retry a failed background job"""
    try:
        job_history = frappe.get_doc("Background Job History", job_id)
        
        if job_history.status != "Failed":
            return False, "Job is not in failed state"
        
        # Re-enqueue with same parameters
        enqueue(
            job_history.method,
            **frappe.parse_json(job_history.kwargs),
            queue=job_history.queue,
            timeout=job_history.timeout
        )
        
        return True, "Job re-queued successfully"
        
    except Exception as e:
        return False, f"Failed to retry job: {str(e)}"
```

### 8.4 Worker Process Management

**Understanding Worker Architecture**

```python
# Frappe worker configuration and monitoring

# bench/config.py - Worker configuration
worker_config = {
    "default": {
        "workers": 4,           # Number of worker processes
        "timeout": 300,         # Default job timeout (5 minutes)
        "max_jobs_per_worker": 100
    },
    "long": {
        "workers": 2,           # Dedicated workers for long jobs
        "timeout": 3600,        # 1 hour timeout
        "max_jobs_per_worker": 10
    },
    "short": {
        "workers": 8,           # More workers for quick jobs
        "timeout": 60,          # 1 minute timeout
        "max_jobs_per_worker": 500
    }
}

# Monitoring worker health
def check_worker_health():
    """Monitor background worker processes"""
    try:
        jobs = get_jobs()
        worker_stats = {}
        
        for queue_name, queue_jobs in jobs.items():
            worker_stats[queue_name] = {
                "running_jobs": len(queue_jobs),
                "queue_config": worker_config.get(queue_name, {})
            }
        
        # Check for stuck jobs
        for queue_name, stats in worker_stats.items():
            max_workers = stats["queue_config"].get("workers", 4)
            if stats["running_jobs"] > max_workers * 10:  # 10x threshold
                frappe.log_error(
                    f"Queue {queue_name} has {stats['running_jobs']} jobs, "
                    f"but only {max_workers} workers. Possible worker issue."
                )
        
        return worker_stats
        
    except Exception as e:
        frappe.log_error(f"Worker health check failed: {str(e)}")
        return {}
```

### 8.5 Email Queue Management

**Professional Email Handling**

```python
# your_app/email_management.py - Advanced email queue handling

import frappe
from frappe.email.doctype.email_queue.email_queue import EmailQueue

@frappe.whitelist()
def send_bulk_notifications(recipients, template, context):
    """
    Send bulk emails using queue to avoid timeouts
    """
    try:
        # 1. Create email queue records
        for recipient in recipients:
            email_queue = frappe.get_doc({
                "doctype": "Email Queue",
                "recipient": recipient,
                "message": frappe.render_template(template, context),
                "subject": context.get("subject", "Notification"),
                "status": "Not Sent"
            })
            email_queue.insert()
        
        # 2. Process queue in background
        enqueue(
            "your_app.email_management.process_email_queue",
            queue="short",
            now=True
        )
        
        frappe.logger().info(f"Queued {len(recipients)} emails for sending")
        
    except Exception as e:
        frappe.log_error(f"Bulk email queuing failed: {str(e)}")

def process_email_queue():
    """Process pending emails in queue"""
    try:
        # Get pending emails (batch of 50)
        pending_emails = frappe.get_all("Email Queue",
            filters={"status": "Not Sent"},
            fields=["name", "recipient", "message", "subject"],
            limit=50
        )
        
        for email in pending_emails:
            try:
                # Send email
                frappe.sendmail(
                    recipients=[email.recipient],
                    subject=email.subject,
                    message=email.message,
                    reference_doctype="Email Queue",
                    reference_name=email.name
                )
                
                # Mark as sent
                frappe.db.set_value("Email Queue", email.name, "status", "Sent")
                
            except Exception as e:
                # Mark as failed
                frappe.db.set_value("Email Queue", email.name, 
                    "status", "Failed")
                frappe.log_error(f"Failed to send email {email.name}: {str(e)}")
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Email queue processing failed: {str(e)}")

def setup_email_digest():
    """
    Setup daily/weekly email digest for notifications
    """
    # Create digest preferences
    pass
```

### 8.6 Error Handling and Logging

**Robust Error Management**

```python
# your_app/error_handling.py - Comprehensive error handling

import frappe
import traceback
from frappe.utils import now

class CustomError(Exception):
    """Base class for custom application errors"""
    def __init__(self, message, error_code=None, context=None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        super().__init__(message)

def handle_hook_error(hook_name, doc, exception):
    """
    Standardized error handling for hook functions
    """
    error_context = {
        "hook_name": hook_name,
        "document_type": doc.doctype,
        "document_name": doc.name,
        "user": frappe.session.user,
        "timestamp": now(),
        "traceback": traceback.format_exc()
    }
    
    # Log with structured data
    frappe.log_error(
        message=f"Hook '{hook_name}' failed for {doc.doctype} {doc.name}: {str(exception)}",
        title=f"Hook Error: {hook_name}",
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        data=error_context
    )
    
    # Optionally notify admin
    if is_critical_error(exception):
        notify_admin_on_error(hook_name, doc, exception, error_context)

def is_critical_error(exception):
    """Determine if error requires admin notification"""
    critical_errors = [
        "DatabaseConnectionError",
        "PaymentProcessingError", 
        "DataIntegrityError"
    ]
    return any(error in str(type(exception)) for error in critical_errors)

def notify_admin_on_error(hook_name, doc, exception, context):
    """Send admin notification for critical errors"""
    admin_users = frappe.get_all("User",
        filters={"role": "System Manager"},
        fields=["email"]
    )
    
    admin_emails = [user.email for user in admin_users if user.email]
    
    if admin_emails:
        frappe.sendmail(
            recipients=admin_emails,
            subject=f"Critical Error in {hook_name}",
            template="critical_error_notification",
            args=dict(
                hook_name=hook_name,
                document=f"{doc.doctype} {doc.name}",
                error_message=str(exception),
                context=context
            )
        )
```

## 🛠️ Practical Exercises

### Exercise 8.1: Create Custom Hook System

Create a custom hook that:
1. Triggers on Customer creation
2. Creates a welcome task
3. Sends notification email
4. Logs activity

### Exercise 8.2: Build Scheduled Report System

Implement a scheduler that:
1. Runs daily at 6 AM
2. Generates sales summary report
3. Emails to management
4. Handles errors gracefully

### Exercise 8.3: Background Job Processing

Create a background job that:
1. Processes large data import
2. Shows progress updates
3. Handles interruptions
4. Notifies on completion

## 🤔 Thought Questions

1. How do you handle hook failures without blocking document operations?
2. When should you use background jobs vs synchronous processing?
3. How do you monitor and maintain scheduled jobs?
4. What are the security considerations for whitelisted methods?

## 📖 Further Reading

- [Frappe Hooks Documentation](https://frappeframework.com/docs/user/en/hooks)
- [Background Jobs Guide](https://frappeframework.com/docs/user/en/background_jobs)
- [Email Queue System](https://frappeframework.com/docs/user/en/email)

## 🎯 Chapter Summary

Server hooks and schedulers provide powerful automation capabilities:

- **Hooks** enable cross-application event handling
- **Schedulers** provide reliable time-based automation  
- **Background jobs** handle long-running tasks efficiently
- **Email queues** ensure reliable communication
- **Error handling** maintains system stability

---

**Next Chapter**: Understanding and implementing the permissions system.
