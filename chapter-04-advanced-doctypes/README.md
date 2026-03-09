# Chapter 4: Advanced DocType Design

## 🎯 Learning Objectives

By the end of this chapter, you will master:

- DocType types: Master, Transaction, Child Table, Single
- Advanced naming series and autoname patterns
- All field types and their specific use cases
- The Meta system and how DocType metadata works
- Property Setters for overriding field properties
- Matrix child tables and dynamic field generation

## 📚 Chapter Topics

### 4.1 DocType Types Deep Dive

#### Master DocTypes

Master DocTypes represent core data entities that are referenced throughout the system.

```python
# Example: Customer Master
{
    "doctype": "DocType",
    "name": "Customer",
    "module": "Selling",
    "is_submittable": 0,
    "istable": 0,
    "naming_rule": "By fieldname",
    "autoname": "field:customer_name",
    "fields": [
        {
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "label": "Customer Name",
            "reqd": 1,
            "unique": 1
        },
        {
            "fieldname": "customer_group",
            "fieldtype": "Link",
            "options": "Customer Group",
            "reqd": 1
        }
    ]
}
```

**Characteristics:**
- Not submittable (no workflow states)
- Often have unique constraints
- Serve as lookup sources for other DocTypes
- Typically have long lifecycles

#### Transaction DocTypes

Transaction DocTypes represent business transactions that go through approval workflows.

```python
# Example: Sales Order
{
    "doctype": "DocType",
    "name": "Sales Order",
    "module": "Selling",
    "is_submittable": 1,
    "istable": 0,
    "naming_rule": "By fieldname",
    "autoname": "SO-.YYYY.-.#####",
    "fields": [
        {
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "reqd": 1,
            "change_on_update": 1
        },
        {
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "default": "Today",
            "reqd": 1
        }
    ]
}
```

**Characteristics:**
- Submittable with workflow states (Draft, Submitted, Cancelled)
- Often have child tables for line items
- Include financial implications
- Have audit trails and permissions

#### Child Table DocTypes

Child tables store multiple related records within a parent document.

```python
# Example: Sales Order Item
{
    "doctype": "DocType",
    "name": "Sales Order Item",
    "module": "Selling",
    "is_submittable": 0,
    "istable": 1,
    "fields": [
        {
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "in_list_view": 1,
            "reqd": 1
        },
        {
            "fieldname": "qty",
            "fieldtype": "Float",
            "in_list_view": 1,
            "reqd": 1
        },
        {
            "fieldname": "rate",
            "fieldtype": "Currency",
            "in_list_view": 1,
            "reqd": 1
        }
    ]
}
```

**Characteristics:**
- Always marked as `istable: 1`
- Cannot be submitted independently
- Must be linked from parent DocType
- Support bulk operations

#### Single DocTypes

Single DocTypes store configuration or singleton data.

```python
# Example: System Settings
{
    "doctype": "DocType",
    "name": "System Settings",
    "module": "Core",
    "is_submittable": 0,
    "istable": 0,
    "is_single": 1,
    "fields": [
        {
            "fieldname": "default_currency",
            "fieldtype": "Link",
            "options": "Currency",
            "label": "Default Currency"
        },
        {
            "fieldname": "enable_notifications",
            "fieldtype": "Check",
            "label": "Enable Notifications"
        }
    ]
}
```

**Characteristics:**
- Only one record exists
- No naming convention needed
- Used for system-wide settings
- Accessed via `frappe.get_single()`

### 4.2 Advanced Naming Series

#### Autoname Patterns

```python
# Different naming patterns
patterns = {
    "Sequential": "#####",                    # 1, 2, 3...
    "Year-based": "INV-.YYYY.-.#####",       # INV-2023-00001
    "Month-based": "EXP-.YYYY.MM.-.####",    # EXP-2023.01-0001
    "Field-based": "field:customer_name",    # Uses field value
    "Mixed": "PO-.####.-.field:supplier",    # PO-0001-SupplierName
    "Date-based": "DOC-.DD.MM.YYYY.-.####",   # DOC-10.03.2026-0001
    "Random": "######",                      # Random 6-digit number
}
```

#### Custom Naming Logic

```python
# Custom naming function in controller
def autoname(self):
    if self.customer_type == "Government":
        self.name = f"GOV-{self.customer_name[:3].upper()}-{frappe.utils.random_string(4)}"
    else:
        self.name = f"COM-{self.customer_name[:3].upper()}-{frappe.utils.random_string(4)}"
```

#### Naming Series Management

```python
# Create naming series
def create_naming_series():
    series = [
        "INV-.YYYY.-.#####",
        "PO-.YYYY.MM.-.####",
        "EXP-.YYYY.-.#####"
    ]
    
    for s in series:
        if not frappe.db.exists("Series", s):
            frappe.get_doc({
                "doctype": "Series",
                "name": s,
                "current": 0
            }).insert()
```

### 4.3 Field Types In Depth

#### Basic Field Types

```python
basic_fields = {
    "Data": {
        "description": "Text input field",
        "example": {"fieldtype": "Data", "label": "Name"},
        "validation": "max_length=140"
    },
    "Link": {
        "description": "Reference to another DocType",
        "example": {"fieldtype": "Link", "options": "Customer"},
        "features": ["search", "filters", "depends_on"]
    },
    "Select": {
        "description": "Dropdown selection",
        "example": {"fieldtype": "Select", "options": "Low\nMedium\nHigh"},
        "validation": "options must be newline-separated"
    },
    "Check": {
        "description": "Boolean checkbox",
        "example": {"fieldtype": "Check", "label": "Active"},
        "default": 0
    }
}
```

#### Advanced Field Types

```python
advanced_fields = {
    "Table": {
        "description": "Child table link",
        "example": {"fieldtype": "Table", "options": "Sales Order Item"},
        "features": ["add_multiple", "bulk_edit"]
    },
    "Table MultiSelect": {
        "description": "Multi-select from child table",
        "example": {"fieldtype": "Table MultiSelect", "options": "Item"},
        "use_case": "Product selection with variants"
    },
    "Dynamic Link": {
        "description": "Link to multiple DocTypes",
        "example": {
            "fieldtype": "Dynamic Link",
            "options": "reference_doctype",
            "fieldname": "reference_name"
        }
    },
    "HTML": {
        "description": "Rich text content",
        "example": {"fieldtype": "HTML", "options": "<h1>Static Content</h1>"},
        "use_case": "Instructions, help text"
    }
}
```

#### Specialized Field Types

```python
specialized_fields = {
    "Currency": {
        "description": "Monetary values",
        "example": {"fieldtype": "Currency", "options": "currency"},
        "features": ["formatting", "conversion", "precision"]
    },
    "Percent": {
        "description": "Percentage values",
        "example": {"fieldtype": "Percent", "precision": "2"},
        "validation": "0-100 range"
    },
    "Date": {
        "description": "Date picker",
        "example": {"fieldtype": "Date", "default": "Today"},
        "features": ["calendar", "range", "validation"]
    },
    "Datetime": {
        "description": "Date and time",
        "example": {"fieldtype": "Datetime", "default": "Now"},
        "features": ["timezone", "formatting"]
    },
    "Time": {
        "description": "Time picker",
        "example": {"fieldtype": "Time"},
        "format": "24-hour"
    }
}
```

#### File and Media Fields

```python
media_fields = {
    "Attach": {
        "description": "File attachment",
        "example": {"fieldtype": "Attach", "label": "Document"},
        "features": ["upload", "preview", "validation"]
    },
    "Attach Image": {
        "description": "Image attachment",
        "example": {"fieldtype": "Attach Image", "label": "Photo"},
        "features": ["thumbnail", "resize", "validation"]
    },
    "Image": {
        "description": "Image display",
        "example": {"fieldtype": "Image", "options": "photo"},
        "features": ["display", "sizing", "responsive"]
    }
}
```

### 4.4 The Meta System

#### How Metadata is Stored

```python
# DocType metadata structure
metadata_structure = {
    "DocType": {
        "table": "tabDocType",
        "key_fields": ["name", "module", "custom", "istable"],
        "relationships": {
            "fields": "DocField",
            "permissions": "DocPerm",
            "actions": "DocAction"
        }
    },
    "DocField": {
        "table": "tabDocField",
        "key_fields": ["parent", "fieldtype", "fieldname", "label"],
        "relationships": {
            "options": "various DocTypes",
            "depends_on": "conditional logic"
        }
    }
}
```

#### Loading Metadata

```python
# How Frappe loads DocType metadata
def load_doctype_meta(doctype):
    # Load from database
    meta = frappe.get_doc('DocType', doctype)
    
    # Cache for performance
    frappe.cache().hset('doctype_meta', doctype, meta.as_dict())
    
    # Process field relationships
    for field in meta.get('fields', []):
        if field.fieldtype == 'Link':
            field._options = field.options
    
    return meta
```

#### Custom Metadata

```python
# Adding custom metadata
def add_custom_metadata():
    # Custom field properties
    custom_properties = {
        "validation": {
            "min_length": 5,
            "max_length": 100,
            "pattern": r"^[A-Za-z0-9\s]+$"
        },
        "ui": {
            "width": "full",
            "css_class": "custom-field",
            "help_text": "Enter alphanumeric characters only"
        }
    }
    
    return custom_properties
```

### 4.5 Property Setters

#### Overriding Field Properties

```python
# Using Property Setters to customize fields
def create_property_setters():
    property_setters = [
        {
            "doctype": "Property Setter",
            "doc_type": "Sales Order",
            "property": "label",
            "property_type": "Data",
            "field_name": "customer",
            "value": "Client Name",
            "__newname": "Sales Order-label-customer-Client Name"
        },
        {
            "doctype": "Property Setter",
            "doc_type": "Sales Order",
            "property": "reqd",
            "property_type": "Check",
            "field_name": "delivery_date",
            "value": "1",
            "__newname": "Sales Order-reqd-delivery_date-1"
        }
    ]
    
    for ps in property_setters:
        if not frappe.db.exists("Property Setter", ps["__newname"]):
            frappe.get_doc(ps).insert()
```

#### Dynamic Property Setters

```python
# Create property setters programmatically
def set_field_properties(doctype, fieldname, properties):
    for prop, value in properties.items():
        ps_name = f"{doctype}-{prop}-{fieldname}-{value}"
        
        if not frappe.db.exists("Property Setter", ps_name):
            frappe.get_doc({
                "doctype": "Property Setter",
                "doc_type": doctype,
                "field_name": fieldname,
                "property": prop,
                "property_type": get_property_type(prop),
                "value": str(value)
            }).insert()
```

### 4.6 Matrix Child Tables

#### Creating Matrix Fields

```python
# Matrix child table configuration
matrix_config = {
    "doctype": "DocType",
    "name": "Price Matrix",
    "istable": 1,
    "fields": [
        {
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "in_list_view": 1,
            "reqd": 1
        },
        {
            "fieldname": "price_list",
            "fieldtype": "Link",
            "options": "Price List",
            "in_list_view": 1,
            "reqd": 1
        },
        {
            "fieldname": "price",
            "fieldtype": "Currency",
            "in_list_view": 1,
            "reqd": 1
        }
    ]
}
```

#### Dynamic Matrix Generation

```python
# Generate matrix based on data
def generate_price_matrix():
    item_groups = frappe.get_all("Item Group", pluck="name")
    price_lists = frappe.get_all("Price List", pluck="name")
    
    matrix = []
    for group in item_groups:
        for price_list in price_lists:
            matrix.append({
                "item_group": group,
                "price_list": price_list,
                "price": 0
            })
    
    return matrix
```

#### Matrix Validation

```python
# Validate matrix data
def validate_matrix(doc):
    matrix_data = doc.get("price_matrix", [])
    
    # Check for duplicates
    seen = set()
    for row in matrix_data:
        key = (row.item_group, row.price_list)
        if key in seen:
            frappe.throw(f"Duplicate entry for {row.item_group} in {row.price_list}")
        seen.add(key)
    
    # Validate prices
    for row in matrix_data:
        if row.price < 0:
            frappe.throw(f"Price cannot be negative for {row.item_group}")
```

## 🛠️ Practical Exercises

### Exercise 4.1: Create Advanced DocType

Create a comprehensive DocType with:
- Multiple field types
- Custom naming series
- Property setters
- Validation logic

### Exercise 4.2: Implement Matrix Child Table

Build a matrix system for:
- Multi-dimensional data
- Dynamic generation
- Validation rules

### Exercise 4.3: Customize Existing DocType

Use property setters to:
- Modify field properties
- Add custom validation
- Enhance user experience

## 🚀 Best Practices

### DocType Design

- **Choose the right DocType type** based on use case
- **Use consistent naming conventions** across your app
- **Implement proper validation** at the field level
- **Design for scalability** with future requirements in mind

### Field Management

- **Use appropriate field types** for data validation
- **Implement field dependencies** for dynamic forms
- **Add helpful descriptions** and placeholders
- **Consider mobile responsiveness** in field layout

### Performance Optimization

- **Minimize custom fields** in high-traffic DocTypes
- **Use efficient indexing** for frequently queried fields
- **Cache metadata** for faster loading
- **Optimize child table queries** with proper filters

## 📖 Further Reading

- [DocType API Reference](https://frappeframework.com/docs/user/en/api/doc)
- [Field Types Documentation](https://frappeframework.com/docs/user/en/doctype/field-types)
- [Property Setter Guide](https://frappeframework.com/docs/user/en/doctype/property-setter)

## 🎯 Chapter Summary

Advanced DocType design is fundamental to building robust ERPNext applications:

- **DocType types** define behavior and lifecycle
- **Naming series** provide flexible document identification
- **Field types** ensure data integrity and user experience
- **Meta system** manages all DocType metadata efficiently
- **Property setters** enable customization without core modifications
- **Matrix tables** handle complex multi-dimensional data

---

**Next Chapter**: Deep dive into controller methods and document lifecycle.
