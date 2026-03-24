# Chapter 9: The Permissions System for Developers

## 🎯 Learning Objectives

By the end of this chapter, you will master:
- **How to design** role-based access control for custom apps
- **Implementing** DocType-level and field-level permissions
- **Understanding** row-level permissions with match conditions
- **Creating** custom permission checks in code
- **Optimizing** permission queries for performance

## 📚 Chapter Topics

### 9.1 Role-Based Access Control Architecture

**Understanding the Permission Hierarchy**

```python
# Frappe permission system architecture
Permission Levels:
1. System Level (Global permissions)
2. App Level (App access)  
3. DocType Level (CRUD permissions)
4. Field Level (Field access)
5. Row Level (Document access)
6. Custom Level (Business logic)
```

**Core Permission DocTypes**

```python
# Key permission-related DocTypes
permission_doctypes = {
    "Role": "Defines user roles and permissions",
    "Role Profile": "Templates for role assignments",
    "Permission Rule": "Advanced permission conditions", 
    "User Permission": "User-specific restrictions",
    "Custom Permission": "Business-specific permissions"
}

# Permission flow
# User -> Role Profiles -> Roles -> Permission Rules -> Document Access
```

**Setting Up Roles Programmatically**

```python
# your_app/setup.py - Role creation and configuration

import frappe

def create_custom_roles():
    """Create custom roles for the application"""
    
    # 1. Asset Manager Role
    if not frappe.db.exists("Role", "Asset Manager"):
        asset_manager = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Asset Manager",
            "desk_access": 1,
            "is_standard": 1,
            "restrict_to_domain": "Assets"
        })
        asset_manager.insert()
        
        # Set up DocType permissions
        setup_asset_manager_permissions(asset_manager.name)
    
    # 2. Asset Viewer Role  
    if not frappe.db.exists("Role", "Asset Viewer"):
        asset_viewer = frappe.get_doc({
            "doctype": "Role", 
            "role_name": "Asset Viewer",
            "desk_access": 1,
            "is_standard": 1,
            "restrict_to_domain": "Assets"
        })
        asset_viewer.insert()
        
        setup_asset_viewer_permissions(asset_viewer.name)
    
    # 3. Department Head Role
    if not frappe.db.exists("Role", "Department Head"):
        dept_head = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Department Head", 
            "desk_access": 1,
            "is_standard": 1
        })
        dept_head.insert()
        
        setup_department_head_permissions(dept_head.name)

def setup_asset_manager_permissions(role):
    """Configure permissions for Asset Manager role"""
    
    # Asset DocType - Full access
    permissions = [
        {
            "doctype": "Custom DocPerm",
            "parent": "Asset",
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1,
            "amend": 1,
            "report": 1,
            "export": 1,
            "print": 1,
            "email": 1,
            "import": 1,
            "set_user_permissions": 1,
            "if_owner": 0,
            "permlevel": 0
        },
        # Asset Assignment - Full access
        {
            "doctype": "Custom DocPerm",
            "parent": "Asset Assignment",
            "parenttype": "DocType", 
            "parentfield": "permissions",
            "role": role,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1,
            "amend": 1,
            "permlevel": 0
        }
    ]
    
    for perm in permissions:
        if not frappe.db.exists("Custom DocPerm", {
            "parent": perm["parent"],
            "role": role
        }):
            frappe.get_doc(perm).insert()

def setup_asset_viewer_permissions(role):
    """Configure permissions for Asset Viewer role - read-only"""
    
    permissions = [
        {
            "doctype": "Custom DocPerm",
            "parent": "Asset",
            "parenttype": "DocType",
            "parentfield": "permissions", 
            "role": role,
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "print": 1,
            "email": 1,
            "import": 0,
            "permlevel": 0
        }
    ]
    
    for perm in permissions:
        if not frappe.db.exists("Custom DocPerm", {
            "parent": perm["parent"],
            "role": role
        }):
            frappe.get_doc(perm).insert()
```

### 9.2 DocType-Level Permissions

**Understanding Permission Levels**

```python
# Permission levels (permlevel) concept
# permlevel 0: Document level access
# permlevel 1: Child table level access
# permlevel 2+: Nested child table access

# Example: Sales Order with multiple permission levels
sales_order_permissions = {
    "permlevel 0": {
        "description": "Main Sales Order document",
        "fields": ["customer", "transaction_date", "grand_total"],
        "access": "Full CRUD for Sales Team"
    },
    "permlevel 1": {
        "description": "Sales Order Items child table", 
        "fields": ["item_code", "qty", "rate"],
        "access": "Read-only for Finance Team"
    }
}
```

**Advanced Permission Configuration**

```python
# your_app/permissions.py - Advanced permission setup

import frappe

def configure_doctype_permissions():
    """Configure comprehensive DocType permissions"""
    
    # 1. Asset DocType - Role-based matrix
    asset_permissions = {
        "Asset Manager": {
            "read": 1, "write": 1, "create": 1, "delete": 1,
            "submit": 1, "cancel": 1, "amend": 1,
            "report": 1, "export": 1, "print": 1, "email": 1
        },
        "Asset Viewer": {
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "submit": 0, "cancel": 0, "amend": 0,
            "report": 1, "export": 1, "print": 1, "email": 1
        },
        "Department Head": {
            "read": 1, "write": 1, "create": 0, "delete": 0,
            "submit": 0, "cancel": 0, "amend": 0,
            "report": 1, "export": 1, "print": 1, "email": 1,
            "if_owner": 1  # Only own department's assets
        }
    }
    
    for role, permissions in asset_permissions.items():
        update_doctype_permissions("Asset", role, permissions)
    
    # 2. Asset Assignment DocType - Separate permissions
    assignment_permissions = {
        "Asset Manager": {
            "read": 1, "write": 1, "create": 1, "delete": 1,
            "submit": 1, "cancel": 1, "amend": 1
        },
        "Employee": {
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "submit": 0, "cancel": 0, "amend": 0,
            "if_owner": 1  # Only own assignments
        }
    }
    
    for role, permissions in assignment_permissions.items():
        update_doctype_permissions("Asset Assignment", role, permissions)

def update_doctype_permissions(doctype, role, permissions):
    """Update or create DocType permissions"""
    
    # Check if permission exists
    existing = frappe.db.exists("Custom DocPerm", {
        "parent": doctype,
        "role": role,
        "permlevel": 0
    })
    
    if existing:
        # Update existing permission
        perm_doc = frappe.get_doc("Custom DocPerm", existing)
        for key, value in permissions.items():
            setattr(perm_doc, key, value)
        perm_doc.save()
    else:
        # Create new permission
        perm_doc = frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": doctype,
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            "permlevel": 0,
            **permissions
        })
        perm_doc.insert()
```

**Conditional Permissions with Property Setters**

```python
# Using property setters for dynamic permissions

def setup_conditional_permissions():
    """Set up conditional field access based on user role"""
    
    # 1. Hide sensitive fields for certain roles
    sensitive_fields = {
        "Asset": {
            "purchase_cost": ["Asset Viewer", "Employee"],
            "maintenance_cost": ["Asset Viewer", "Employee"] 
        },
        "Asset Assignment": {
            "notes": ["Employee"]
        }
    }
    
    for doctype, fields in sensitive_fields.items():
        for field, restricted_roles in fields.items():
            for role in restricted_roles:
                create_property_setter(
                    doctype=doctype,
                    fieldname=field,
                    property_type="Hidden",
                    value=1,
                    property_name=f"hidden_for_role_{role}"
                )
    
    # 2. Make fields read-only for certain roles
    readonly_fields = {
        "Asset": {
            "asset_code": ["All"],  # Read-only for everyone
            "current_status": ["Asset Viewer", "Employee"]
        }
    }
    
    for doctype, fields in readonly_fields.items():
        for field, roles in fields.items():
            for role in roles:
                if role == "All":
                    # Apply to all users
                    create_property_setter(
                        doctype=doctype,
                        fieldname=field,
                        property_type="Read Only",
                        value=1,
                        property_name="read_only"
                    )
                else:
                    # Role-specific
                    create_property_setter(
                        doctype=doctype,
                        fieldname=field,
                        property_type="Read Only",
                        value=1,
                        property_name=f"read_only_for_role_{role}"
                    )

def create_property_setter(doctype, fieldname, property_type, value, property_name):
    """Create property setter for field permissions"""
    
    if frappe.db.exists("Property Setter", {
        "doc_type": doctype,
        "property": property_name,
        "field_name": fieldname
    }):
        return  # Already exists
    
    property_setter = frappe.get_doc({
        "doctype": "Property Setter",
        "doc_type": doctype,
        "property": property_name,
        "property_type": property_type,
        "field_name": fieldname,
        "value": str(value),
        "is_system_generated": 0
    })
    property_setter.insert()
```

### 9.3 Field-Level Permissions

**Implementing Field Access Control**

```python
# your_app/field_permissions.py - Field-level access control

import frappe

def get_field_permissions(doctype, user=None):
    """Get field permissions for a user and doctype"""
    
    if not user:
        user = frappe.session.user
    
    user_roles = frappe.get_roles(user)
    field_permissions = {}
    
    # Get all fields for the doctype
    meta = frappe.get_meta(doctype)
    fields = meta.get("fields")
    
    for field in fields:
        field_name = field.get("fieldname")
        if not field_name:
            continue
        
        # Check property setters for this field
        field_perms = check_field_property_setters(doctype, field_name, user_roles)
        
        # Check custom field permissions
        custom_perms = check_custom_field_permissions(doctype, field_name, user_roles)
        
        # Merge permissions
        field_permissions[field_name] = {
            "readable": not field_perms.get("hidden", False),
            "writable": not field_perms.get("read_only", False) and not field_perms.get("hidden", False),
            "required": field.get("reqd", 0),
            "custom_permissions": custom_perms
        }
    
    return field_permissions

def check_field_property_setters(doctype, fieldname, user_roles):
    """Check property setters for field access"""
    
    permissions = {
        "hidden": False,
        "read_only": False
    }
    
    # Get property setters for this field
    property_setters = frappe.get_all("Property Setter",
        filters={
            "doc_type": doctype,
            "field_name": fieldname
        },
        fields=["property", "value"]
    )
    
    for ps in property_setters:
        property_name = ps.property
        value = ps.value == "1"
        
        if property_name == "read_only":
            permissions["read_only"] = value
        elif property_name == "hidden":
            permissions["hidden"] = value
        elif property_name.startswith("hidden_for_role_"):
            role = property_name.replace("hidden_for_role_", "")
            if role in user_roles and value:
                permissions["hidden"] = True
        elif property_name.startswith("read_only_for_role_"):
            role = property_name.replace("read_only_for_role_", "")
            if role in user_roles and value:
                permissions["read_only"] = True
    
    return permissions

def check_custom_field_permissions(doctype, fieldname, user_roles):
    """Check custom business logic for field permissions"""
    
    custom_perms = {}
    
    # Example: Only managers can see cost fields
    if "cost" in fieldname.lower():
        if "Manager" not in user_roles and "System Manager" not in user_roles:
            custom_perms["hidden"] = True
    
    # Example: Only HR can see salary fields
    if "salary" in fieldname.lower():
        if "HR Manager" not in user_roles and "HR User" not in user_roles:
            custom_perms["hidden"] = True
    
    # Example: Department-based field access
    if "department" in fieldname.lower():
        user_department = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "department")
        if user_department:
            custom_perms["filter"] = {"department": user_department}
    
    return custom_perms
```

**Client-Side Field Permission Enforcement**

```javascript
// public/js/field_permissions.js - Client-side permission enforcement

frappe.ui.form.on('Asset', {
    refresh: function(frm) {
        // Apply field permissions on form refresh
        apply_field_permissions(frm);
    },
    
    onload: function(frm) {
        // Check permissions on form load
        check_form_permissions(frm);
    }
});

function apply_field_permissions(frm) {
    // Get field permissions from server
    frappe.call({
        method: 'your_app.permissions.get_field_permissions',
        args: {
            doctype: frm.doctype,
            user: frappe.session.user
        },
        callback: function(r) {
            if (r.message) {
                let permissions = r.message;
                
                // Apply permissions to each field
                Object.keys(permissions).forEach(function(fieldname) {
                    let perm = permissions[fieldname];
                    let field = frm.get_field(fieldname);
                    
                    if (field) {
                        // Hide field if not readable
                        if (!perm.readable) {
                            field.df.hidden = 1;
                            field.refresh();
                        }
                        
                        // Make read-only if not writable
                        if (!perm.writable && perm.readable) {
                            field.df.read_only = 1;
                            field.refresh();
                        }
                        
                        // Apply custom filters
                        if (perm.custom_permissions && perm.custom_permissions.filter) {
                            // For Link fields, apply filters
                            if (field.df.fieldtype === 'Link') {
                                field.df.filters = perm.custom_permissions.filter;
                                field.refresh();
                            }
                        }
                    }
                });
                
                frm.refresh_fields();
            }
        }
    });
}

function check_form_permissions(frm) {
    // Check if user has permission to view this document
    if (!frm.doc.__islocal) {
        frappe.call({
            method: 'frappe.client.has_permission',
            args: {
                doctype: frm.doctype,
                name: frm.docname,
                ptype: 'read'
            },
            callback: function(r) {
                if (!r.message) {
                    frappe.msgprint({
                        title: __('Permission Denied'),
                        message: __('You do not have permission to view this document'),
                        indicator: 'red'
                    });
                    frappe.set_route('List', frm.doctype);
                }
            }
        });
    }
}
```

### 9.4 Row-Level Permissions

**User Permissions for Document Access**

```python
# your_app/row_permissions.py - Row-level permission implementation

import frappe

def setup_user_permissions():
    """Configure user-specific document restrictions"""
    
    # 1. Department-based asset access
    setup_department_user_permissions()
    
    # 2. Project-based document access
    setup_project_user_permissions()
    
    # 3. Customer-based access for sales team
    setup_customer_user_permissions()

def setup_department_user_permissions():
    """Allow users to access only their department's assets"""
    
    # Get all employees with their departments
    employees = frappe.get_all("Employee",
        filters={"status": "Active"},
        fields=["name", "user_id", "department"]
    )
    
    for employee in employees:
        if not employee.user_id or not employee.department:
            continue
        
        # Create user permission for department
        if not frappe.db.exists("User Permission", {
            "user": employee.user_id,
            "allow": "Department",
            "for_value": employee.department,
            "applicable_for": "Asset"
        }):
            user_perm = frappe.get_doc({
                "doctype": "User Permission",
                "user": employee.user_id,
                "allow": "Department", 
                "for_value": employee.department,
                "applicable_for": "Asset",
                "is_default": 1
            })
            user_perm.insert()

def setup_project_user_permissions():
    """Allow users to access only assigned project documents"""
    
    # Get all project assignments
    project_assignments = frappe.get_all("Project Assignment",
        fields=["user", "project"]
    )
    
    for assignment in project_assignments:
        if not assignment.user or not assignment.project:
            continue
        
        # Create user permission for project
        if not frappe.db.exists("User Permission", {
            "user": assignment.user,
            "allow": "Project",
            "for_value": assignment.project
        }):
            user_perm = frappe.get_doc({
                "doctype": "User Permission",
                "user": assignment.user,
                "allow": "Project",
                "for_value": assignment.project,
                "is_default": 0
            })
            user_perm.insert()

def setup_customer_user_permissions():
    """Sales team can only access their assigned customers"""
    
    # Get all customer assignments
    customer_assignments = frappe.get_all("Customer Team",
        fields=["user", "customer"]
    )
    
    for assignment in customer_assignments:
        if not assignment.user or not assignment.customer:
            continue
        
        # Create user permission for customer
        if not frappe.db.exists("User Permission", {
            "user": assignment.user,
            "allow": "Customer",
            "for_value": assignment.customer
        }):
            user_perm = frappe.get_doc({
                "doctype": "User Permission",
                "user": assignment.user,
                "allow": "Customer",
                "for_value": assignment.customer,
                "is_default": 0
            })
            user_perm.insert()
```

**Match Conditions for Dynamic Row Permissions**

```python
# your_app/match_conditions.py - Advanced match conditions

import frappe

def get_asset_match_conditions(user):
    """Generate match conditions for asset access"""
    
    conditions = []
    
    # 1. Department-based condition
    user_department = frappe.db.get_value("Employee", {"user_id": user}, "department")
    if user_department:
        conditions.append(f"department = '{user_department}'")
    
    # 2. Role-based conditions
    user_roles = frappe.get_roles(user)
    
    if "Asset Manager" in user_roles:
        # Asset managers can see all assets in their company
        user_company = frappe.db.get_value("Employee", {"user_id": user}, "company")
        if user_company:
            conditions.append(f"company = '{user_company}'")
    
    elif "Department Head" in user_roles:
        # Department heads can see assets in their department
        if user_department:
            conditions.append(f"department = '{user_department}'")
    
    else:
        # Regular employees can only see assigned assets
        assigned_assets = frappe.get_all("Asset Assignment",
            filters={"assigned_to": user, "docstatus": 1},
            pluck="asset"
        )
        if assigned_assets:
            asset_list = "', '".join(assigned_assets)
            conditions.append(f"name IN ('{asset_list}')")
        else:
            # No assigned assets - return false condition
            conditions.append("1 = 0")
    
    # Combine conditions
    if conditions:
        return " AND ".join(conditions)
    else:
        return "1 = 0"  # No access by default

def get_sales_order_match_conditions(user):
    """Generate match conditions for sales order access"""
    
    conditions = []
    user_roles = frappe.get_roles(user)
    
    # 1. Sales team can see their orders
    if "Sales User" in user_roles or "Sales Manager" in user_roles:
        # Get customer assignments
        assigned_customers = frappe.get_all("Customer Team",
            filters={"user": user},
            pluck="customer"
        )
        
        if assigned_customers:
            customer_list = "', '".join(assigned_customers)
            conditions.append(f"customer IN ('{customer_list}')")
        else:
            conditions.append("1 = 0")  # No assigned customers
    
    # 2. Managers can see all orders in their territory
    elif "Sales Manager" in user_roles:
        user_territory = frappe.db.get_value("Employee", {"user_id": user}, "territory")
        if user_territory:
            conditions.append(f"territory = '{user_territory}'")
    
    # 3. Finance can see all submitted orders
    elif "Accounts User" in user_roles or "Accounts Manager" in user_roles:
        conditions.append("docstatus = 1")  # Only submitted orders
    
    # Combine conditions
    if conditions:
        return " AND ".join(conditions)
    else:
        return "1 = 0"

# Register match conditions in hooks.py
permission_query_conditions = {
    "Asset": "your_app.match_conditions.get_asset_match_conditions",
    "Sales Order": "your_app.match_conditions.get_sales_order_match_conditions"
}
```

### 9.5 Custom Permission Checks

**Business Logic Permission Validation**

```python
# your_app/custom_permissions.py - Custom business logic permissions

import frappe

def check_asset_assignment_permission(doc, user=None):
    """
    Custom permission check for asset assignments
    - Only asset managers can assign assets
    - Users can only assign assets from their department
    - Cannot assign already assigned assets
    """
    
    if not user:
        user = frappe.session.user
    
    user_roles = frappe.get_roles(user)
    user_department = frappe.db.get_value("Employee", {"user_id": user}, "department")
    
    # 1. Check if user has asset management role
    if "Asset Manager" not in user_roles and "System Manager" not in user_roles:
        return False, "Only Asset Managers can assign assets"
    
    # 2. Check department access
    if doc.asset:
        asset_department = frappe.db.get_value("Asset", doc.asset, "department")
        if asset_department != user_department and "System Manager" not in user_roles:
            return False, f"You can only assign assets from your department ({user_department})"
    
    # 3. Check if asset is already assigned
    if doc.asset and doc.assigned_to:
        existing_assignment = frappe.db.exists("Asset Assignment", {
            "asset": doc.asset,
            "assigned_to": doc.assigned_to,
            "docstatus": 1,
            "name": ["!=", doc.name] if doc.name else ("!=", "")
        })
        
        if existing_assignment:
            return False, "Asset is already assigned to this user"
    
    # 4. Check if assignee is valid employee
    if doc.assigned_to:
        if not frappe.db.exists("Employee", {"user_id": doc.assigned_to}):
            return False, "Assignee must be a valid employee"
    
    return True, "Permission granted"

def check_sales_order_approval_permission(doc, user=None):
    """
    Custom permission for sales order approval
    - Only managers can approve orders above certain value
    - Territory-based approval limits
    """
    
    if not user:
        user = frappe.session.user
    
    # Check if this is an approval action
    if doc.docstatus != 1:  # Not submitted
        return True, "Not an approval action"
    
    # Get approval limits for user
    approval_limits = get_user_approval_limits(user)
    
    if not approval_limits:
        return False, "No approval limits configured for user"
    
    # Check territory
    if doc.territory not in approval_limits.get("territories", []):
        return False, f"Not authorized to approve orders in territory {doc.territory}"
    
    # Check amount limit
    max_amount = approval_limits.get("max_amount", 0)
    if doc.grand_total > max_amount:
        return False, f"Order amount {doc.grand_total} exceeds approval limit {max_amount}"
    
    return True, "Approval permission granted"

def get_user_approval_limits(user):
    """Get approval limits for a user"""
    
    # Check role-based limits first
    user_roles = frappe.get_roles(user)
    
    if "Sales Manager" in user_roles:
        return {
            "territories": get_user_territories(user),
            "max_amount": 100000  # $100K limit
        }
    elif "Sales Director" in user_roles:
        return {
            "territories": ["All"],  # All territories
            "max_amount": 500000  # $500K limit
        }
    elif "System Manager" in user_roles:
        return {
            "territories": ["All"],
            "max_amount": 1000000  # $1M limit
        }
    
    return None

def get_user_territories(user):
    """Get territories assigned to user"""
    
    territories = frappe.get_all("Sales Person",
        filters={"user": user},
        pluck="territory"
    )
    
    return territories if territories else []

# Register custom permission checks in hooks.py
doc_events = {
    "Asset Assignment": {
        "validate": "your_app.custom_permissions.validate_asset_assignment"
    },
    "Sales Order": {
        "before_submit": "your_app.custom_permissions.validate_sales_order_approval"
    }
}

def validate_asset_assignment(doc, method):
    """Validate asset assignment permissions"""
    
    has_permission, message = check_asset_assignment_permission(doc)
    
    if not has_permission:
        frappe.throw(
            msg=message,
            title="Permission Denied",
            exc=frappe.PermissionError
        )

def validate_sales_order_approval(doc, method):
    """Validate sales order approval permissions"""
    
    has_permission, message = check_sales_order_approval_permission(doc)
    
    if not has_permission:
        frappe.throw(
            msg=message,
            title="Approval Denied",
            exc=frappe.PermissionError
        )
```

### 9.6 Permission Query Optimization

**Performance Optimization for Permission Checks**

```python
# your_app/permission_optimization.py - Permission query optimization

import frappe
from frappe.utils import cint, now_datetime
import redis

class PermissionCache:
    """Cache for permission queries to improve performance"""
    
    def __init__(self):
        self.redis_client = frappe.cache()
        self.cache_ttl = 300  # 5 minutes
    
    def get_user_permissions(self, user, doctype):
        """Get cached permissions for user and doctype"""
        
        cache_key = f"user_permissions:{user}:{doctype}"
        cached_data = self.redis_client.get_value(cache_key)
        
        if cached_data:
            return frappe.parse_json(cached_data)
        
        # Generate permissions
        permissions = self.generate_permissions(user, doctype)
        
        # Cache the result
        self.redis_client.set_value(
            cache_key, 
            frappe.as_json(permissions), 
            expires_in_sec=self.cache_ttl
        )
        
        return permissions
    
    def generate_permissions(self, user, doctype):
        """Generate permission data for user and doctype"""
        
        permissions = {
            "read": False,
            "write": False,
            "create": False,
            "delete": False,
            "submit": False,
            "cancel": False,
            "match_conditions": "",
            "field_permissions": {}
        }
        
        # Get user roles
        user_roles = frappe.get_roles(user)
        
        # Check DocType permissions
        doctype_perms = frappe.get_all("Custom DocPerm",
            filters={
                "parent": doctype,
                "role": ["in", user_roles]
            },
            fields=["*"]
        )
        
        for perm in doctype_perms:
            # Aggregate permissions (any role with permission grants access)
            for key in ["read", "write", "create", "delete", "submit", "cancel"]:
                if cint(perm.get(key, 0)):
                    permissions[key] = True
        
        # Get match conditions
        if doctype in frappe.permission_query_conditions:
            match_condition_func = frappe.permission_query_conditions[doctype]
            try:
                permissions["match_conditions"] = match_condition_func(user)
            except Exception as e:
                frappe.log_error(f"Error in match condition for {doctype}: {str(e)}")
                permissions["match_conditions"] = "1 = 0"
        
        # Get field permissions
        permissions["field_permissions"] = get_field_permissions(doctype, user)
        
        return permissions
    
    def invalidate_user_cache(self, user):
        """Invalidate cache for a specific user"""
        
        # Get all cache keys for user
        pattern = f"user_permissions:{user}:*"
        keys = self.redis_client.get_keys(pattern)
        
        # Delete all user-specific cache entries
        for key in keys:
            self.redis_client.delete_value(key)

# Global permission cache instance
permission_cache = PermissionCache()

def optimized_has_permission(doctype, name, ptype="read", user=None):
    """Optimized permission check with caching"""
    
    if not user:
        user = frappe.session.user
    
    # Get cached permissions
    permissions = permission_cache.get_user_permissions(user, doctype)
    
    # Check basic permission
    if not permissions.get(ptype, False):
        return False
    
    # If match conditions exist, check them
    if permissions.get("match_conditions"):
        try:
            # Build and execute match condition query
            query = f"""
                SELECT name FROM `tab{doctype}` 
                WHERE name = %s AND ({permissions['match_conditions']})
            """
            result = frappe.db.sql(query, (name,), as_dict=True)
            return len(result) > 0
        except Exception as e:
            frappe.log_error(f"Error checking match conditions: {str(e)}")
            return False
    
    return True

# Hook into Frappe's permission system
def override_permission_checks():
    """Override standard permission checks with optimized versions"""
    
    # This would be called from hooks.py app_include_js
    # or through patch to replace standard functions
    pass
```

**Database Index Optimization**

```python
# your_app/db_optimization.py - Database optimization for permissions

import frappe

def create_permission_indexes():
    """Create database indexes to optimize permission queries"""
    
    # 1. Index for user permissions
    if not frappe.db.exists("Index", {"table": "tabUser Permission", "column": "user"}):
        frappe.db.sql("""
            CREATE INDEX idx_user_permission_user 
            ON `tabUser Permission` (user)
        """)
    
    if not frappe.db.exists("Index", {"table": "tabUser Permission", "column": "allow"}):
        frappe.db.sql("""
            CREATE INDEX idx_user_permission_allow 
            ON `tabUser Permission` (allow, for_value)
        """)
    
    # 2. Index for role-based permissions
    if not frappe.db.exists("Index", {"table": "tabCustom DocPerm", "column": "role"}):
        frappe.db.sql("""
            CREATE INDEX idx_docperm_role 
            ON `tabCustom DocPerm` (role, parent)
        """)
    
    # 3. Index for common permission fields
    permission_doctypes = ["Asset", "Sales Order", "Customer", "Project"]
    
    for doctype in permission_doctypes:
        table_name = f"tab{doctype}"
        
        # Department index (common permission filter)
        if not frappe.db.exists("Index", {"table": table_name, "column": "department"}):
            frappe.db.sql(f"""
                CREATE INDEX idx_{doctype.lower()}_department 
                ON `{table_name}` (department)
            """)
        
        # Company index
        if not frappe.db.exists("Index", {"table": table_name, "column": "company"}):
            frappe.db.sql(f"""
                CREATE INDEX idx_{doctype.lower()}_company 
                ON `{table_name}` (company)
            """)
        
        # Owner index (for if_owner permissions)
        if not frappe.db.exists("Index", {"table": table_name, "column": "owner"}):
            frappe.db.sql(f"""
                CREATE INDEX idx_{doctype.lower()}_owner 
                ON `{table_name}` (owner)
            """)

def analyze_permission_queries():
    """Analyze slow permission queries and suggest optimizations"""
    
    # Get slow queries from log
    slow_queries = frappe.get_all("Query Log",
        filters={
            "query": ["like", "%WHERE%"],
            "duration": [">", 1.0]  # Queries taking more than 1 second
        },
        fields=["query", "duration", "timestamp"],
        order_by="duration desc",
        limit=20
    )
    
    optimization_suggestions = []
    
    for query_log in slow_queries:
        query = query_log.query
        
        # Check for permission-related queries
        if any(keyword in query.lower() for keyword in ["role", "permission", "user"]):
            
            # Analyze query pattern
            if "WHERE" in query and "IN" in query:
                # Might benefit from index on IN clause columns
                optimization_suggestions.append({
                    "query": query,
                    "duration": query_log.duration,
                    "suggestion": "Consider adding index on columns used in IN clause",
                    "priority": "High" if query_log.duration > 5.0 else "Medium"
                })
            
            elif "JOIN" in query and "Custom DocPerm" in query:
                # Permission join optimization
                optimization_suggestions.append({
                    "query": query,
                    "duration": query_log.duration,
                    "suggestion": "Consider caching role permissions",
                    "priority": "Medium"
                })
    
    return optimization_suggestions
```

## 🛠️ Practical Exercises

### Exercise 9.1: Create Role-Based Permission System

Create a complete permission system for an asset management app:
1. Define custom roles (Asset Manager, Asset Viewer, Department Head)
2. Configure DocType permissions
3. Set up field-level restrictions
4. Implement row-level access control

### Exercise 9.2: Implement Match Conditions

Create dynamic match conditions for:
1. Department-based document access
2. Territory-based sales restrictions
3. Project-based access control
4. Customer-specific permissions

### Exercise 9.3: Optimize Permission Queries

Implement performance optimizations:
1. Add database indexes for permission fields
2. Create permission caching system
3. Analyze and optimize slow permission queries
4. Monitor permission system performance

## 🤔 Thought Questions

1. How do you balance security with usability in permission design?
2. When should you use row-level permissions vs DocType-level permissions?
3. How do you handle permission inheritance in hierarchical structures?
4. What are the performance implications of complex permission rules?

## 📖 Further Reading

- [Frappe Permissions Documentation](https://frappeframework.com/docs/user/en/permissions)
- [User Permissions Guide](https://frappeframework.com/docs/user/en/user-permissions)
- [Role Management Best Practices](https://frappeframework.com/docs/user/en/role-management)

## 🎯 Chapter Summary

The permissions system provides comprehensive access control:

- **Role-based access** provides scalable permission management
- **DocType permissions** control document-level access
- **Field permissions** enable granular data protection
- **Row-level permissions** restrict access to specific records
- **Custom permissions** enforce business-specific rules
- **Performance optimization** ensures responsive user experience

---

**Next Chapter**: Building custom print formats with Jinja templating.


---

## 📌 Addendum: User Permissions ("Allow" Mechanism) & Decision Flowchart

### User Permissions — The "Allow" Mechanism

**Role Permissions** control *what DocTypes* a role can access.  **User Permissions** control *which specific records* a user can see within those DocTypes.

A User Permission entry says: *"User X may only access documents where field Y equals value Z."*

```python
# Create a User Permission programmatically
frappe.get_doc({
    'doctype': 'User Permission',
    'user': 'alice@example.com',
    'allow': 'Company',          # The DocType being restricted
    'for_value': 'Acme Corp',    # The specific value allowed
    'applicable_for': '',        # Leave blank = applies to ALL doctypes
                                 # Or set to a specific DocType e.g. 'Sales Order'
    'is_default': 1
}).insert(ignore_permissions=True)
```

**How it works at query time:**

When `alice@example.com` runs `frappe.get_all('Sales Order', ...)`, Frappe automatically appends `AND company = 'Acme Corp'` to the SQL query — she never sees orders from other companies.

**Key rules:**
- User Permissions are additive — if a user has *no* User Permission for a DocType, they see *all* records (subject to role permissions).
- Once *any* User Permission exists for a user+DocType combination, it acts as a whitelist — only matching records are visible.
- `applicable_for` scopes the restriction to a single DocType; leaving it blank applies it everywhere the `allow` DocType appears as a Link field.

```python
# Check user permissions programmatically
user_perms = frappe.get_user_permissions('alice@example.com')
# Returns: {'Company': [{'doc': 'Acme Corp', 'is_default': 1}], ...}

# Test if a specific document is accessible
frappe.has_permission('Sales Order', 'read', 'SO-0001', user='alice@example.com')
```

### Permissions Decision Flowchart

```
  User requests access to Document D
              │
              ▼
  ┌─────────────────────────────┐
  │ Does user have a Role with  │
  │ READ permission on DocType? │
  └──────────┬──────────────────┘
             │ No → ❌ DENIED
             │ Yes
             ▼
  ┌─────────────────────────────────────┐
  │ Is the DocType restricted by        │
  │ permission_query_conditions hook?   │
  └──────────┬──────────────────────────┘
             │ Yes → apply SQL condition
             │ No  → continue
             ▼
  ┌──────────────────────────────────────┐
  │ Does the user have any User          │
  │ Permission entries for this DocType  │
  │ (directly or via a Link field)?      │
  └──────────┬───────────────────────────┘
             │ No  → ✅ ALLOWED (role permission sufficient)
             │ Yes
             ▼
  ┌──────────────────────────────────────┐
  │ Does Document D match at least one   │
  │ of the user's User Permission values?│
  └──────────┬───────────────────────────┘
             │ No  → ❌ DENIED
             │ Yes
             ▼
  ┌──────────────────────────────────────┐
  │ Is the field permlevel accessible    │
  │ for the user's role?                 │
  └──────────┬───────────────────────────┘
             │ No  → field hidden/read-only
             │ Yes
             ▼
           ✅ ALLOWED
```

**Debugging permissions:**

```python
# In bench console — trace why a user cannot see a document
frappe.set_user('alice@example.com')
print(frappe.has_permission('Sales Order', 'read', 'SO-0001'))
print(frappe.get_user_permissions())

# Check the generated SQL condition
from frappe.permissions import get_doc_condition
print(get_doc_condition('Sales Order', 'alice@example.com'))
```


---

## 📌 Addendum: Roles and Permissions — Complete Guide

### Core Concepts

**Permission** — a specific right to perform an action on a DocType. Stored as `DocPerm` records.

**Role** — a collection of permissions grouped together. Users inherit all permissions from all their roles (permissions are additive).

**Role Profile** — a collection of roles assigned as a group (simplifies user management).

### Permission Types

| Permission | Description |
|-----------|-------------|
| **Read** | View documents and fields |
| **Write** | Modify documents and fields |
| **Create** | Create new documents |
| **Delete** | Remove documents |
| **Submit** | Submit documents (submittable DocTypes) |
| **Cancel** | Cancel submitted documents |
| **Amend** | Create amended versions of cancelled documents |
| **Report** | Access reports |
| **Export** | Export data |
| **Import** | Import data |
| **Print** | Print documents |
| **Email** | Email documents |
| **Share** | Share documents with other users |

### Permission Hierarchy

1. **DocType Level** — can the user access this DocType at all?
2. **Field Level** — which fields can the user see/edit? (controlled by `permlevel`)
3. **Document Level** — which specific records can the user access? (User Permissions)

### Permission Levels (permlevel)

Permission levels (0-9) control field-level access. Each field has a `permlevel` property.

**Critical rules:**
- Level 0 is mandatory for document access — without it, users cannot access the document at all
- Permission levels are NOT cumulative — having level 2 does NOT grant access to level 0 or 1
- You must explicitly grant permissions at each level you want users to access

**Example setup:**

```
Fields:
- customer (permlevel: 0)
- order_date (permlevel: 0)
- discount_percentage (permlevel: 1)
- profit_margin (permlevel: 2)

Sales User Role:
- Level 0: Read, Write, Create
- Level 1: Read, Write
- Level 2: Read only

Result: Sales User can read/write customer and order_date,
        read/write discount_percentage, but only read profit_margin
```

**Best practice permlevel scheme:**
- Level 0: Basic fields everyone needs (customer, date, total)
- Level 1: Standard editable fields (discount, notes)
- Level 2: Sensitive fields (profit margin, cost)
- Level 3+: Admin-only fields

### User Permissions (Document-Level)

User Permissions restrict users to specific document records based on linked document values.

```
User Permission: User="john@example.com", Allow="Customer", For Value="ABC Corp"
→ John can only see documents where customer = "ABC Corp"
```

This works by automatically adding WHERE conditions to database queries.

### Permission Management Tools

1. **Permission Inspector** (`/app/permission-inspector`) — debug why a user has/doesn't have a specific permission
2. **Role Permission Manager** (`/app/permission-manager`) — review and manage permissions for a role on a DocType
3. **Role Permission for Page and Report** (`/app/role-permission-for-page-and-report`) — control access to pages and reports
4. **User Permissions** (`/app/user-permission`) — restrict users to specific document records

### Permission Checking Flow

```
User requests document
    ↓
Is Administrator? → Yes → Grant all access
    ↓ No
Check role permissions (permlevel 0)
    ↓
Apply "if owner" restrictions if applicable
    ↓
Apply User Permissions filtering
    ↓
Filter fields by permlevel access
    ↓
Return permitted documents/fields
```

### "If Owner" Permission

When "If Owner" is checked on a permission rule, the permission only applies when `doc.owner == user`. This enables owner-based access control.

Note: "If Owner" cannot be used with "Create" permission (documents don't have owners until created).

### Programmatic Permission Checks

```python
# Check if user has permission
frappe.has_permission("Customer", "write", doc=customer_doc)

# Get all permissions for current user on a DocType
perms = frappe.get_doc("DocType", "Customer").get_permissions()

# Custom permission hook
def has_permission(doc, user):
    if doc.owner == user:
        return True
    return False

# In hooks.py
has_permission = {
    "Customer": "my_app.permissions.has_permission"
}

# Add query conditions based on permissions
def permission_query_conditions(user):
    return f"`tabCustomer`.owner = '{user}'"

permission_query_conditions = {
    "Customer": "my_app.permissions.permission_query_conditions"
}
```

### Row-Level Permissions

```python
# Restrict users to their own records
def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return ""  # No restrictions for System Manager
    
    return f"`tabSales Order`.owner = '{user}'"
```


---

## Addendum: Source Article Insights

### Roles, Permissions, and the Permission Hierarchy

Frappe's access control operates at three levels:

1. **DocType level** — can the user access this DocType at all?
2. **Field level** — which fields can the user see/edit?
3. **Document level** — which specific records can the user access?

**Permissions are additive across roles.** A user with multiple roles gets the union of all permissions from all their roles.

```python
# Checking permissions programmatically
import frappe

# Check if current user has read permission on a DocType
frappe.has_permission("Sales Order", "read")

# Check permission for a specific document
frappe.has_permission("Sales Order", "write", doc=so_doc)

# Get all permissions for current user on a DocType
perms = frappe.permissions.get_role_permissions(
    frappe.get_meta("Sales Order"),
    frappe.session.user
)
# Returns: {"read": 1, "write": 1, "create": 0, ...}
```

---

### Permission Levels (permlevel)

Permission levels (0–9) control field-level access. **They are NOT cumulative** — having level 2 does not grant level 0 or 1 access. Each level must be explicitly granted.

**Level 0 is mandatory** — without it, users cannot access the document at all.

```
Typical permlevel scheme:
  Level 0: Standard fields (customer, date, total) — everyone with access
  Level 1: Editable fields (discount, notes) — sales staff
  Level 2: Sensitive fields (profit margin, cost) — managers only
  Level 3+: Admin-only fields
```

**Setting up permission rules for a role:**

```
Role: Sales User
  - Level 0: Read, Write, Create
  - Level 1: Read, Write
  - Level 2: Read only

Role: Sales Manager
  - Level 0: Read, Write, Create, Delete
  - Level 1: Read, Write
  - Level 2: Read, Write   ← can edit sensitive fields
```

**How the system checks field access (Python):**

```python
# frappe/model/meta.py (simplified)
def get_permlevel_access(self, permission_type="read"):
    """Returns list of permlevels where user has the given permission."""
    allowed_permlevels = []
    for perm in self.get_permissions():
        if perm.role in user_roles and perm.get(permission_type):
            if perm.permlevel not in allowed_permlevels:
                allowed_permlevels.append(perm.permlevel)
    return allowed_permlevels  # e.g., [0, 1, 2]

# Field access check — exact match, not range
def has_permlevel_access_to(self, fieldname, permission_type="read"):
    df = self.meta.get_field(fieldname)
    return df.permlevel in self.get_permlevel_access(permission_type)
```

---

### permission_query_conditions Hook

This hook adds SQL WHERE conditions to database queries automatically. It filters data **at the database level** — users never see records they shouldn't.

**When it's called:** Any `frappe.get_list()`, `frappe.get_all()`, or List View query.

```python
# my_app/doctype/sales_order/sales_order.py

def get_permission_query_conditions(user):
    """
    Returns SQL WHERE condition to filter Sales Orders by user's company.
    Called automatically when querying Sales Orders.
    """
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return None  # No filtering for admin

    # Get user's company
    user_company = frappe.db.get_value("User", user, "company")
    if user_company:
        return f"`tabSales Order`.`company` = {frappe.db.escape(user_company)}"

    return None
```

```python
# hooks.py
permission_query_conditions = {
    "Sales Order": "my_app.doctype.sales_order.sales_order.get_permission_query_conditions"
}
```

**Important rules:**
- Return a SQL condition string **without** the `WHERE` keyword
- Always use `frappe.db.escape()` to prevent SQL injection
- Return `None` or `""` for no filtering (e.g., Administrator)
- Use backtick-quoted table names: `` `tabDocType`.`fieldname` ``

**More complex example (from Frappe core — Dashboard Chart):**

```python
def get_permission_query_conditions(user):
    if user == "Administrator":
        return None

    allowed_doctypes = frappe.permissions.get_doctypes_with_read()
    allowed_reports = get_allowed_report_names()

    return f"""
        ((`tabDashboard Chart`.`chart_type` in ('Count', 'Sum', 'Average')
        and `tabDashboard Chart`.`document_type` in ({allowed_doctypes}))
        or
        (`tabDashboard Chart`.`chart_type` = 'Report'
        and `tabDashboard Chart`.`report_name` in ({allowed_reports})))
    """
```

---

### has_permission Hook

This hook checks access to a **specific document**. It's called when a user tries to open, save, or delete a document.

**Key behavior:**
- Return `True` to allow access
- Return `False` to deny access (even if the user has role-based permission)
- Return `None` to defer to default permission checks
- This hook can only **deny** permissions, not grant new ones beyond what roles allow
- Called in **reverse order** (last registered hook runs first)

```python
# my_app/doctype/sales_order/sales_order.py

def has_permission(doc, ptype, user, debug=False):
    """
    Custom permission check for Sales Orders.
    Users can only submit orders they created.
    """
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    # For submit permission: only the creator can submit
    if ptype == "submit":
        if doc.owner == user:
            return True
        return False  # Deny submit for non-owners

    # For other permissions: use default role-based checks
    return None
```

```python
# hooks.py
has_permission = {
    "Sales Order": "my_app.doctype.sales_order.sales_order.has_permission"
}
```

---

### Using Both Hooks Together

The most secure pattern uses both hooks: `permission_query_conditions` filters lists, `has_permission` guards individual document access.

```python
# my_app/doctype/asset/asset.py

def get_permission_query_conditions(user):
    """Filter asset list to user's department."""
    if not user:
        user = frappe.session.user
    if user == "Administrator":
        return None

    dept = frappe.db.get_value("Employee", {"user_id": user}, "department")
    if dept:
        return f"`tabAsset`.`department` = {frappe.db.escape(dept)}"
    return None


def has_permission(doc, ptype, user, debug=False):
    """Allow write only if asset is in user's department."""
    if not user:
        user = frappe.session.user
    if user == "Administrator":
        return True

    if ptype in ("write", "delete"):
        dept = frappe.db.get_value("Employee", {"user_id": user}, "department")
        if doc.department == dept:
            return True
        return False

    return None  # Default for read and other types
```

```python
# hooks.py
permission_query_conditions = {
    "Asset": "my_app.doctype.asset.asset.get_permission_query_conditions"
}
has_permission = {
    "Asset": "my_app.doctype.asset.asset.has_permission"
}
```

---

### User Permissions (Document-Level Filtering)

User Permissions restrict a user to specific document records based on linked field values. They work by automatically adding WHERE conditions to queries.

```python
# Create a User Permission programmatically
frappe.get_doc({
    "doctype": "User Permission",
    "user": "john@example.com",
    "allow": "Customer",           # The DocType being restricted
    "for_value": "ABC Corp",       # The specific record allowed
    "apply_to_all_doctypes": 0,
    "applicable_for": "Sales Order"  # Only apply to Sales Orders
}).insert()
```

**How it works:** When John queries Sales Orders, Frappe automatically adds:
```sql
WHERE `tabSales Order`.`customer` = 'ABC Corp'
```

**Key differences between the two hooks:**

| | `permission_query_conditions` | `has_permission` |
|---|---|---|
| Level | DocType (all docs) | Single document |
| Returns | SQL WHERE string | True/False/None |
| Performance | Database-level (fast) | Application-level |
| Use case | Filter lists/reports | Guard document access |

---

### Permission Management Tools

**Permission Inspector** (`/app/permission-inspector`): Debug why a user has or doesn't have a specific permission. Shows all roles, all matching rules, and the final decision.

**Role Permission Manager** (`/app/permission-manager`): View and edit all permission rules for a role on a DocType.

**User Permissions** (`/app/user-permission`): Manage document-level restrictions per user.

```python
# Useful permission utilities
import frappe.permissions

# Get all doctypes a user can read
readable = frappe.permissions.get_doctypes_with_read()

# Get role permissions for a doctype
meta = frappe.get_meta("Sales Order")
perms = frappe.permissions.get_role_permissions(meta, frappe.session.user)

# Check if user has a specific role
frappe.user.has_role("Sales Manager")

# Get all roles for current user
roles = frappe.get_roles()
```
