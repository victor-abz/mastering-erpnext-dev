# Chapter 5: The Controller – Document Class Deep Dive

## 🎯 Learning Objectives

By the end of this chapter, you will master:

- The complete Document lifecycle from initialization to database commit
- All controller hooks and their execution order
- Proper usage of `doc.get_value()`, `doc.get()`, and direct attribute access
- Database internals: `db_insert()`, `db_update()` methods
- Preventing infinite loops in hooks
- Managing document state with `doc.docstatus`

## 📚 Chapter Topics

### 5.1 Document Lifecycle Overview

#### The Complete Journey

```python
# Document lifecycle flow
document_lifecycle = {
    "1. Creation": {
        "methods": ["__init__", "load_from_db"],
        "description": "Document instance creation and data loading"
    },
    "2. Validation": {
        "methods": ["validate", "validate_save"],
        "description": "Data validation and business rules"
    },
    "3. Pre-Save": {
        "methods": ["before_save", "before_insert"],
        "description": "Pre-save processing and transformations"
    },
    "4. Save": {
        "methods": ["db_insert", "db_update"],
        "description": "Database operations"
    },
    "5. Post-Save": {
        "methods": ["on_update", "after_save"],
        "description": "Post-save processing and notifications"
    },
    "6. Submission": {
        "methods": ["before_submit", "on_submit", "after_submit"],
        "description": "Document submission workflow"
    },
    "7. Cancellation": {
        "methods": ["before_cancel", "on_cancel", "after_cancel"],
        "description": "Document cancellation workflow"
    },
    "8. Deletion": {
        "methods": ["before_trash", "on_trash", "after_trash"],
        "description": "Document deletion workflow"
    }
}
```

#### State Transitions

```python
# Document state diagram
state_transitions = {
    "Draft (0)": {
        "can_submit": True,
        "can_save": True,
        "can_cancel": False,
        "can_delete": True
    },
    "Submitted (1)": {
        "can_submit": False,
        "can_save": True,
        "can_cancel": True,
        "can_delete": False
    },
    "Cancelled (2)": {
        "can_submit": False,
        "can_save": True,
        "can_cancel": False,
        "can_delete": True
    }
}
```

### 5.2 Controller Hooks in Order

#### Initialization Hooks

```python
class CustomDocument(Document):
    def __init__(self, *args, **kwargs):
        """Called when document is instantiated"""
        super().__init__(*args, **kwargs)
        
        # Custom initialization
        self._custom_data = {}
        self._validation_errors = []
        
        # Load custom data if document exists
        if not self.is_new():
            self.load_custom_data()
    
    def load_custom_data(self):
        """Load custom data related to this document"""
        if hasattr(self, 'customer'):
            # Load customer-specific data
            pass
    
    def autoname(self):
        """Generate document name automatically"""
        if not self.name:
            # Custom naming logic
            if self.customer_type == "Government":
                self.name = f"GOV-{self.customer_name[:3].upper()}-{frappe.utils.random_string(4)}"
            else:
                self.name = f"COM-{self.customer_name[:3].upper()}-{frappe.utils.random_string(4)}"
```

#### Validation Hooks

```python
class CustomDocument(Document):
    def validate(self):
        """Main validation hook - called before save"""
        # Required field validation
        self.validate_required_fields()
        
        # Business logic validation
        self.validate_business_rules()
        
        # Data consistency validation
        self.validate_data_consistency()
        
        # Custom validation
        self.validate_custom_logic()
    
    def validate_required_fields(self):
        """Validate required fields"""
        required_fields = ['customer', 'transaction_date', 'items']
        
        for field in required_fields:
            if not self.get(field):
                frappe.throw(f"{field.title()} is required")
    
    def validate_business_rules(self):
        """Validate business rules"""
        # Example: Cannot create sales order for inactive customer
        if self.customer:
            customer_status = frappe.db.get_value('Customer', self.customer, 'status')
            if customer_status != 'Active':
                frappe.throw("Cannot create Sales Order for inactive customer")
        
        # Example: Validate transaction date
        if self.transaction_date and self.transaction_date > frappe.utils.today():
            frappe.throw("Transaction date cannot be in the future")
    
    def validate_data_consistency(self):
        """Validate data consistency across fields"""
        # Validate child table consistency
        for item in self.get('items', []):
            if item.qty <= 0:
                frappe.throw(f"Quantity must be greater than 0 for item {item.item_code}")
            
            if item.rate <= 0:
                frappe.throw(f"Rate must be greater than 0 for item {item.item_code}")
    
    def validate_custom_logic(self):
        """Custom validation logic"""
        # Example: Validate total amount
        total_amount = sum(item.qty * item.rate for item in self.get('items', []))
        if abs(total_amount - self.total_amount) > 0.01:
            frappe.throw("Total amount doesn't match sum of item amounts")
```

#### Pre-Save Hooks

```python
class CustomDocument(Document):
    def before_save(self):
        """Called before document is saved"""
        # Calculate derived fields
        self.calculate_totals()
        
        # Set default values
        self.set_default_values()
        
        # Format data
        self.format_data()
        
        # Audit trail
        self.add_audit_trail()
    
    def before_insert(self):
        """Called before new document is inserted"""
        # Set creation-specific values
        if self.is_new():
            self.creation_date = frappe.utils.now()
            self.created_by = frappe.session.user
            self.document_number = self.generate_document_number()
            
            # Initialize child table fields
            self.initialize_child_tables()
    
    def calculate_totals(self):
        """Calculate totals and derived values"""
        total_amount = 0
        total_quantity = 0
        
        for item in self.get('items', []):
            item.amount = item.qty * item.rate
            total_amount += item.amount
            total_quantity += item.qty
        
        self.total_amount = total_amount
        self.total_quantity = total_quantity
        self.net_total = total_amount - self.discount_amount
    
    def set_default_values(self):
        """Set default values"""
        if not self.transaction_date:
            self.transaction_date = frappe.utils.today()
        
        if not self.fiscal_year:
            self.fiscal_year = frappe.db.get_default('fiscal_year')
    
    def format_data(self):
        """Format data for consistency"""
        if self.customer_name:
            self.customer_name = self.customer_name.title()
        
        # Format phone numbers
        if self.phone:
            self.phone = ''.join(filter(str.isdigit, self.phone))
```

#### Save Hooks

```python
class CustomDocument(Document):
    def on_update(self):
        """Called after document is saved"""
        # Update related documents
        self.update_related_documents()
        
        # Send notifications
        self.send_notifications()
        
        # Update statistics
        self.update_statistics()
        
        # Log activity
        self.log_activity()
    
    def after_save(self):
        """Called after all save operations complete"""
        # Clear cache
        self.clear_cache()
        
        # Trigger webhooks
        self.trigger_webhooks()
        
        # Update search index
        self.update_search_index()
    
    def db_insert(self):
        """Custom database insert logic"""
        # Override for custom insert behavior
        if hasattr(self, 'custom_insert_logic'):
            self.perform_custom_insert()
        else:
            super().db_insert()
    
    def db_update(self):
        """Custom database update logic"""
        # Override for custom update behavior
        if hasattr(self, 'custom_update_logic'):
            self.perform_custom_update()
        else:
            super().db_update()
```

#### Submission Hooks

```python
class CustomDocument(Document):
    def before_submit(self):
        """Called before document submission"""
        # Validate submission requirements
        self.validate_submission_requirements()
        
        # Check permissions
        self.check_submit_permissions()
        
        # Reserve resources
        self.reserve_resources()
        
        # Create accounting entries
        self.create_accounting_entries()
    
    def on_submit(self):
        """Called after document is submitted"""
        # Update inventory
        self.update_inventory()
        
        # Create follow-up tasks
        self.create_follow_up_tasks()
        
        # Send confirmation
        self.send_submission_confirmation()
        
        # Update status in related documents
        self.update_related_status()
    
    def after_submit(self):
        """Called after all submission operations"""
        # Trigger workflows
        self.trigger_workflows()
        
        # Update reporting data
        self.update_reporting_data()
        
        # Archive old data
        self.archive_transaction_data()
```

#### Cancellation Hooks

```python
class CustomDocument(Document):
    def before_cancel(self):
        """Called before document cancellation"""
        # Validate cancellation requirements
        self.validate_cancellation_requirements()
        
        # Check if cancellation is allowed
        self.check_cancellation_allowed()
        
        # Reverse accounting entries
        self.reverse_accounting_entries()
    
    def on_cancel(self):
        """Called after document is cancelled"""
        # Release reserved resources
        self.release_resources()
        
        # Update inventory
        self.reverse_inventory_updates()
        
        # Cancel related documents
        self.cancel_related_documents()
        
        # Send cancellation notification
        self.send_cancellation_notification()
    
    def after_cancel(self):
        """Called after all cancellation operations"""
        # Update statistics
        self.update_cancellation_statistics()
        
        # Clear cache
        self.clear_cancellation_cache()
```

### 5.3 Data Access Methods

#### Understanding the Differences

```python
class DataAccessExample(Document):
    def demonstrate_data_access(self):
        """Different ways to access document data"""
        
        # 1. Direct attribute access (fastest)
        customer_name = self.customer_name
        total_amount = self.total_amount
        
        # 2. Using get() method (safe, with default)
        customer_name = self.get('customer_name', 'Unknown Customer')
        total_amount = self.get('total_amount', 0)
        
        # 3. Using get_value() (with fallback to database)
        customer_name = self.get_value('customer_name')
        total_amount = self.get_value('total_amount')
        
        # 4. Accessing child table data
        for item in self.get('items', []):
            item_code = item.item_code
            quantity = item.get('qty', 0)
        
        # 5. Getting single value from database
        customer_email = frappe.db.get_value('Customer', self.customer, 'email')
        
        # 6. Getting multiple values from database
        customer_data = frappe.db.get_value('Customer', self.customer, 
                                          ['email', 'customer_group', 'territory'])
        if customer_data:
            email, group, territory = customer_data
```

#### Performance Considerations

```python
class PerformanceOptimizedController(Document):
    def efficient_data_access(self):
        """Efficient data access patterns"""
        
        # Good: Batch database queries
        customers = frappe.db.get_all('Customer', 
                                     fields=['name', 'customer_name', 'email'],
                                     filters={'status': 'Active'})
        
        # Bad: Multiple individual queries in loop
        # for item in self.items:
        #     item_name = frappe.db.get_value('Item', item.item_code, 'item_name')
        
        # Good: Single query with IN clause
        item_codes = [item.item_code for item in self.items]
        item_names = frappe.db.get_all('Item',
                                       fields=['name', 'item_name'],
                                       filters={'name': ['in', item_codes]})
        
        # Create lookup dictionary
        item_lookup = {item.name: item.item_name for item in item_names}
        
        # Use lookup in loop
        for item in self.items:
            item.item_name = item_lookup.get(item.item_code)
```

### 5.4 Preventing Infinite Loops

#### Common Loop Scenarios

```python
class LoopPreventionController(Document):
    def safe_update_related(self):
        """Safely update related documents without loops"""
        
        # Method 1: Check if already updating
        if hasattr(self, '_updating_related'):
            return
        
        self._updating_related = True
        try:
            # Update related documents
            for child in self.get('items', []):
                if child.item_code:
                    # Update item statistics
                    self.update_item_stats(child.item_code)
        finally:
            delattr(self, '_updating_related')
    
    def safe_cross_validation(self):
        """Safe cross-document validation"""
        
        # Method 2: Use flag to prevent recursion
        if frappe.flags.in_cross_validation:
            return
        
        frappe.flags.in_cross_validation = True
        try:
            # Cross-validation logic
            self.validate_with_related_docs()
        finally:
            frappe.flags.in_cross_validation = False
    
    def safe_recursive_operation(self):
        """Safe recursive operations"""
        
        # Method 3: Track call stack
        if not hasattr(frappe.local, 'call_stack'):
            frappe.local.call_stack = []
        
        method_name = 'safe_recursive_operation'
        if method_name in frappe.local.call_stack:
            return
        
        frappe.local.call_stack.append(method_name)
        try:
            # Recursive operation
            self.process_related_data()
        finally:
            frappe.local.call_stack.remove(method_name)
```

### 5.5 Managing Document State

#### Understanding docstatus

```python
class DocumentStateController(Document):
    def manage_document_state(self):
        """Manage document state transitions"""
        
        # Current state
        current_state = self.docstatus  # 0=Draft, 1=Submitted, 2=Cancelled
        
        # State-based validation
        if current_state == 0:  # Draft
            self.validate_draft_state()
        elif current_state == 1:  # Submitted
            self.validate_submitted_state()
        elif current_state == 2:  # Cancelled
            self.validate_cancelled_state()
    
    def validate_draft_state(self):
        """Validations for draft state"""
        # Can modify all fields
        # Can add/remove child items
        # Can change customer
        pass
    
    def validate_submitted_state(self):
        """Validations for submitted state"""
        # Limited field changes allowed
        # Cannot modify financial fields
        # Cannot add/remove items
        
        # Example: Only allow status updates
        if self.has_value_changed('status'):
            self.validate_status_change()
        
        # Prevent modification of critical fields
        critical_fields = ['customer', 'transaction_date', 'total_amount']
        for field in critical_fields:
            if self.has_value_changed(field):
                frappe.throw(f"Cannot modify {field} after submission")
    
    def validate_cancelled_state(self):
        """Validations for cancelled state"""
        # Very limited changes allowed
        # Only can add cancellation remarks
        
        if self.has_value_changed('cancellation_remarks'):
            self.validate_cancellation_remarks()
    
    def state_based_operations(self):
        """Perform operations based on document state"""
        
        if self.docstatus == 0:  # Draft
            # Calculate provisional values
            self.calculate_provisional_totals()
            
        elif self.docstatus == 1:  # Submitted
            # Create accounting entries
            self.create_accounting_entries()
            
            # Update inventory
            self.update_inventory()
            
        elif self.docstatus == 2:  # Cancelled
            # Reverse accounting entries
            self.reverse_accounting_entries()
            
            # Restore inventory
            self.restore_inventory()
```

## 🛠️ Practical Exercises

### Exercise 5.1: Complete Controller Implementation

Create a comprehensive controller with:
- All lifecycle hooks
- Proper validation logic
- State management
- Performance optimization

### Exercise 5.2: Loop Prevention

Implement safe cross-document updates:
- Multiple methods for loop prevention
- Proper error handling
- Performance considerations

### Exercise 5.3: State Management

Build a state-aware controller:
- State-based validation
- Conditional operations
- Proper state transitions

## 🚀 Best Practices

### Controller Design

- **Keep methods focused** on single responsibilities
- **Use descriptive method names** for clarity
- **Handle errors gracefully** with meaningful messages
- **Document complex logic** with comments

### Performance Optimization

- **Minimize database queries** in loops
- **Use caching** for frequently accessed data
- **Batch operations** when possible
- **Profile performance** of critical methods

### Error Handling

- **Validate early** to fail fast
- **Provide clear error messages** to users
- **Log errors** for debugging
- **Handle edge cases** gracefully

## 📖 Further Reading

- [Document API Reference](https://frappeframework.com/docs/user/en/api/document)
- [Controller Hooks Guide](https://frappeframework.com/docs/user/en/development/hooks)
- [Database Operations](https://frappeframework.com/docs/user/en/development/database)

## 🎯 Chapter Summary

Mastering controllers is essential for robust Frappe applications:

- **Lifecycle hooks** provide complete control over document behavior
- **Data access methods** offer flexibility with performance considerations
- **Loop prevention** ensures system stability
- **State management** controls document workflows
- **Performance optimization** maintains application responsiveness

---

**Next Chapter**: Mastering the Frappe ORM for efficient database operations.
