# Chapter 6: Mastering the Frappe ORM

## 🎯 Learning Objectives

By the end of this chapter, you will master:

- `frappe.get_doc()`: loading, inserting, and submitting documents
- `frappe.get_all()` vs `frappe.get_list()` vs `frappe.db.get_all()`
- Efficient query writing: `frappe.db.sql()` vs ORM methods
- Understanding joins: `frappe.db.sql` with JOINs vs Link fields
- Bulk operations: `frappe.db.bulk_insert` and performance considerations
- Database transaction management: `frappe.db.commit`, `rollback`, `savepoint`
- Query optimization: using `explain` and analyzing slow queries

## 📚 Chapter Topics

### 6.1 Understanding the Frappe ORM

#### What is the ORM?

The Object-Relational Mapping (ORM) in Frappe provides a Python interface to interact with the database without writing raw SQL queries. It abstracts database operations and provides a consistent API for data manipulation.

#### ORM Components

```python
# Core ORM components
orm_components = {
    "Document": "Represents a single database record",
    "Database": "Low-level database operations",
    "QueryBuilder": "Dynamic query construction",
    "Transaction": "Database transaction management"
}
```

### 6.2 Document Operations with frappe.get_doc()

#### Loading Documents

```python
# Load existing document
doc = frappe.get_doc('Customer', 'CUST-00001')

# Load document with fields
doc = frappe.get_doc('Customer', 'CUST-00001', ['customer_name', 'email'])

# Load document with filters
doc = frappe.get_doc('Customer', {'email': 'customer@example.com'})

# Load document with custom fields
doc = frappe.get_doc('Customer', 'CUST-00001', fields=['*'])
```

#### Creating New Documents

```python
# Create new document
customer = frappe.new_doc('Customer')
customer.customer_name = 'John Doe'
customer.email = 'john@example.com'
customer.customer_group = 'Individual'
customer.insert()

# Create document with dictionary
customer_data = {
    'doctype': 'Customer',
    'customer_name': 'Jane Smith',
    'email': 'jane@example.com',
    'customer_group': 'Individual'
}
customer = frappe.get_doc(customer_data)
customer.insert()
```

#### Submitting Documents

```python
# Create and submit in one operation
sales_order = frappe.new_doc('Sales Order')
sales_order.customer = 'CUST-00001'
sales_order.transaction_date = frappe.utils.today()
sales_order.append('items', {
    'item_code': 'ITEM-001',
    'qty': 10,
    'rate': 100
})
sales_order.insert()
sales_order.submit()

# Submit existing document
doc = frappe.get_doc('Sales Order', 'SO-00001')
doc.submit()
```

#### Updating Documents

```python
# Load, modify, and save
customer = frappe.get_doc('Customer', 'CUST-00001')
customer.email = 'newemail@example.com'
customer.save()

# Update specific fields
frappe.db.set_value('Customer', 'CUST-00001', 'email', 'newemail@example.com')

# Update multiple fields
frappe.db.set_value('Customer', 'CUST-00001', {
    'email': 'newemail@example.com',
    'phone': '+1234567890'
})
```

### 6.3 Query Methods Comparison

#### frappe.get_all() vs frappe.get_list()

```python
# frappe.get_all() - Returns list of dictionaries
customers = frappe.get_all('Customer', 
    fields=['name', 'customer_name', 'email'],
    filters={'customer_group': 'Individual'},
    order_by='customer_name asc'
)

# Result: [{'name': 'CUST-001', 'customer_name': 'John Doe', 'email': 'john@example.com'}, ...]

# frappe.get_list() - Returns list of dictionaries with additional metadata
customers = frappe.get_list('Customer',
    fields=['name', 'customer_name', 'email'],
    filters={'customer_group': 'Individual'},
    order_by='customer_name asc',
    limit_page_length=20
)

# Result: Same as get_all() but with pagination support
```

#### frappe.db.get_all()

```python
# Direct database access - faster for simple queries
customers = frappe.db.get_all('Customer',
    fields=['name', 'customer_name', 'email'],
    filters={'customer_group': 'Individual'},
    order_by='customer_name asc'
)

# With as_dict parameter
customers = frappe.db.get_all('Customer',
    fields=['name', 'customer_name', 'email'],
    filters={'customer_group': 'Individual'},
    as_dict=True
)
```

#### Performance Comparison

```python
# Method 1: frappe.get_all() - Recommended for most cases
def get_customers_method1():
    return frappe.get_all('Customer', 
        fields=['name', 'customer_name'],
        filters={'customer_group': 'Individual'}
    )

# Method 2: frappe.db.get_all() - Slightly faster for simple queries
def get_customers_method2():
    return frappe.db.get_all('Customer',
        fields=['name', 'customer_name'],
        filters={'customer_group': 'Individual'},
        as_dict=True
    )

# Method 3: Raw SQL - Fastest but less safe
def get_customers_method3():
    return frappe.db.sql("""
        SELECT name, customer_name 
        FROM `tabCustomer` 
        WHERE customer_group = %s
    """, ('Individual',), as_dict=True)
```

### 6.4 Advanced Query Writing

#### Complex Filters

```python
# Multiple conditions
orders = frappe.get_all('Sales Order',
    filters={
        'customer': 'CUST-00001',
        'status': ['!=', 'Closed'],
        'transaction_date': ['>=', '2023-01-01']
    }
)

# OR conditions
orders = frappe.get_all('Sales Order',
    filters=[
        ['customer', '=', 'CUST-00001'],
        ['or', ['status', '=', 'Open'], ['status', '=', 'Overdue']]
    ]
)

# Complex filters with subqueries
orders = frappe.get_all('Sales Order',
    filters=[
        ['customer', 'in', frappe.db.sql_list("""
            SELECT name FROM `tabCustomer` 
            WHERE customer_group = 'Individual'
        """)],
        ['status', '!=', 'Closed']
    ]
)
```

#### Joins and Relationships

```python
# Using Link fields (automatic joins)
orders = frappe.get_all('Sales Order',
    fields=['name', 'customer', 'customer_name'],
    filters={'customer': 'CUST-00001'}
)

# Manual joins with frappe.db.sql
orders_with_details = frappe.db.sql("""
    SELECT 
        so.name as order_name,
        so.customer,
        c.customer_name,
        so.grand_total
    FROM `tabSales Order` so
    JOIN `tabCustomer` c ON so.customer = c.name
    WHERE so.status != 'Closed'
    ORDER BY so.transaction_date DESC
    LIMIT 100
""", as_dict=True)

# Subquery example
customers_with_orders = frappe.db.sql("""
    SELECT DISTINCT c.name, c.customer_name
    FROM `tabCustomer` c
    WHERE EXISTS (
        SELECT 1 FROM `tabSales Order` so 
        WHERE so.customer = c.name 
        AND so.docstatus = 1
    )
""", as_dict=True)
```

#### Aggregations and Grouping

```python
# Simple aggregations
total_sales = frappe.db.get_value('Sales Order', 
    filters={'status': 'Submitted'},
    fieldname='SUM(grand_total)'
)

# Group by operations
sales_by_customer = frappe.db.sql("""
    SELECT 
        customer,
        customer_name,
        COUNT(*) as order_count,
        SUM(grand_total) as total_sales
    FROM `tabSales Order`
    WHERE status = 'Submitted'
    GROUP BY customer, customer_name
    ORDER BY total_sales DESC
    LIMIT 10
""", as_dict=True)

# With HAVING clause
top_customers = frappe.db.sql("""
    SELECT 
        customer,
        customer_name,
        SUM(grand_total) as total_sales
    FROM `tabSales Order`
    WHERE status = 'Submitted'
    GROUP BY customer, customer_name
    HAVING SUM(grand_total) > 10000
    ORDER BY total_sales DESC
""", as_dict=True)
```

### 6.5 Bulk Operations

#### Bulk Insert

```python
# Prepare data for bulk insert
customers_data = []
for i in range(1000):
    customers_data.append({
        'doctype': 'Customer',
        'customer_name': f'Customer {i}',
        'email': f'customer{i}@example.com',
        'customer_group': 'Individual'
    })

# Bulk insert
frappe.db.bulk_insert('Customer', customers_data)

# Bulk insert with specific fields
frappe.db.bulk_insert('Customer', 
    customers_data,
    ignore_duplicates=True
)
```

#### Bulk Update

```python
# Bulk update with SQL
frappe.db.sql("""
    UPDATE `tabCustomer`
    SET customer_group = 'Premium'
    WHERE total_sales > 50000
""")

# Bulk update with values
updates = [
    {'name': 'CUST-001', 'email': 'new1@example.com'},
    {'name': 'CUST-002', 'email': 'new2@example.com'}
]

for update in updates:
    frappe.db.set_value('Customer', update['name'], 'email', update['email'])
```

#### Performance Considerations

```python
# Method 1: Individual inserts (slow)
def slow_insert():
    for i in range(1000):
        customer = frappe.new_doc('Customer')
        customer.customer_name = f'Customer {i}'
        customer.insert()

# Method 2: Bulk insert (fast)
def fast_insert():
    customers_data = []
    for i in range(1000):
        customers_data.append({
            'doctype': 'Customer',
            'customer_name': f'Customer {i}',
            'customer_group': 'Individual'
        })
    frappe.db.bulk_insert('Customer', customers_data)

# Method 3: Raw SQL (fastest)
def fastest_insert():
    values = []
    for i in range(1000):
        values.append(f"(UUID(), NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 'Customer {i}', 'Individual')")
    
    sql = f"""
        INSERT INTO `tabCustomer` 
        (name, creation, modified, modified_by, owner, docstatus, idx, customer_name, customer_group)
        VALUES {','.join(values)}
    """
    frappe.db.sql(sql)
```

### 6.6 Database Transaction Management

#### Basic Transactions

```python
# Simple transaction
def create_customer_with_order():
    try:
        # Start transaction
        frappe.db.begin()
        
        # Create customer
        customer = frappe.new_doc('Customer')
        customer.customer_name = 'John Doe'
        customer.insert()
        
        # Create sales order
        sales_order = frappe.new_doc('Sales Order')
        sales_order.customer = customer.name
        sales_order.append('items', {
            'item_code': 'ITEM-001',
            'qty': 10,
            'rate': 100
        })
        sales_order.insert()
        
        # Commit transaction
        frappe.db.commit()
        
    except Exception as e:
        # Rollback on error
        frappe.db.rollback()
        frappe.log_error(f"Transaction failed: {str(e)}")
        raise
```

#### Savepoints

```python
# Using savepoints for nested transactions
def complex_transaction():
    try:
        frappe.db.begin()
        
        # First savepoint
        frappe.db.savepoint('customer_created')
        
        customer = frappe.new_doc('Customer')
        customer.customer_name = 'John Doe'
        customer.insert()
        
        try:
            # Second savepoint
            frappe.db.savepoint('order_created')
            
            sales_order = frappe.new_doc('Sales Order')
            sales_order.customer = customer.name
            sales_order.insert()
            
            # Simulate error
            if sales_order.grand_total > 10000:
                raise Exception("Order amount too high")
                
        except Exception as e:
            # Rollback to order savepoint
            frappe.db.rollback_to_savepoint('order_created')
            frappe.log_error(f"Order creation failed: {str(e)}")
        
        # Continue with customer creation
        frappe.db.commit()
        
    except Exception as e:
        frappe.db.rollback()
        raise
```

#### Transaction Decorators

```python
# Transaction decorator
def transaction(func):
    def wrapper(*args, **kwargs):
        try:
            frappe.db.begin()
            result = func(*args, **kwargs)
            frappe.db.commit()
            return result
        except Exception as e:
            frappe.db.rollback()
            raise
    return wrapper

# Using the decorator
@transaction
def create_customer_and_order():
    customer = frappe.new_doc('Customer')
    customer.customer_name = 'John Doe'
    customer.insert()
    
    sales_order = frappe.new_doc('Sales Order')
    sales_order.customer = customer.name
    sales_order.insert()
    
    return customer.name, sales_order.name
```

### 6.7 Query Optimization

#### Using EXPLAIN

```python
# Analyze query performance
def analyze_query():
    # Get query execution plan
    explain_result = frappe.db.sql("""
        EXPLAIN SELECT name, customer_name 
        FROM `tabCustomer` 
        WHERE customer_group = 'Individual'
    """)
    
    for row in explain_result:
        print(f"Query Plan: {row}")
    
    # Analyze slow query
    slow_query = """
        SELECT so.name, so.grand_total, c.customer_name
        FROM `tabSales Order` so
        JOIN `tabCustomer` c ON so.customer = c.name
        WHERE so.status = 'Submitted'
        ORDER BY so.transaction_date DESC
        LIMIT 100
    """
    
    explain_slow = frappe.db.sql(f"EXPLAIN {slow_query}")
    for row in explain_slow:
        print(f"Slow Query Plan: {row}")

# Check for missing indexes
def check_indexes():
    # Get table indexes
    indexes = frappe.db.sql("SHOW INDEX FROM `tabCustomer`")
    
    # Check for specific index
    customer_group_index = any(
        idx[2] == 'customer_group' for idx in indexes
    )
    
    if not customer_group_index:
        print("Missing index on customer_group field")
        # Create index
        frappe.db.sql("CREATE INDEX idx_customer_group ON `tabCustomer`(customer_group)")
```

#### Query Optimization Strategies

```python
# Strategy 1: Use specific fields instead of *
def optimized_query_1():
    # Bad: Selects all fields
    customers = frappe.db.sql("SELECT * FROM `tabCustomer` WHERE customer_group = %s", 
                             ('Individual',), as_dict=True)
    
    # Good: Selects only needed fields
    customers = frappe.db.sql("""
        SELECT name, customer_name, email 
        FROM `tabCustomer` 
        WHERE customer_group = %s
    """, ('Individual',), as_dict=True)

# Strategy 2: Use LIMIT for large result sets
def optimized_query_2():
    # Bad: May return thousands of records
    all_orders = frappe.get_all('Sales Order', filters={'status': 'Submitted'})
    
    # Good: Use pagination
    orders = frappe.get_all('Sales Order', 
                           filters={'status': 'Submitted'},
                           limit_page_length=100,
                           start=0)

# Strategy 3: Use EXISTS instead of IN for subqueries
def optimized_query_3():
    # Bad: Slow with large subquery
    customers = frappe.db.sql("""
        SELECT name FROM `tabCustomer` 
        WHERE name IN (
            SELECT DISTINCT customer FROM `tabSales Order`
        )
    """, as_dict=True)
    
    # Good: Uses EXISTS
    customers = frappe.db.sql("""
        SELECT DISTINCT name FROM `tabCustomer` c
        WHERE EXISTS (
            SELECT 1 FROM `tabSales Order` so 
            WHERE so.customer = c.name
        )
    """, as_dict=True)

# Strategy 4: Batch processing for large operations
def optimized_query_4():
    # Bad: Processes all records at once
    all_customers = frappe.get_all('Customer')
    for customer in all_customers:
        # Process customer
        pass
    
    # Good: Process in batches
    batch_size = 100
    offset = 0
    
    while True:
        customers = frappe.get_all('Customer', 
                                   limit_page_length=batch_size,
                                   start=offset)
        if not customers:
            break
            
        for customer in customers:
            # Process customer
            pass
            
        offset += batch_size
```

#### Caching Strategies

```python
# Using Frappe cache
def get_customer_with_cache(customer_id):
    cache_key = f"customer_data_{customer_id}"
    
    # Try to get from cache
    cached_data = frappe.cache().get(cache_key)
    if cached_data:
        return cached_data
    
    # Get from database
    customer = frappe.get_doc('Customer', customer_id)
    customer_data = customer.as_dict()
    
    # Cache for 1 hour
    frappe.cache().set(cache_key, customer_data, expires_in_sec=3600)
    
    return customer_data

# Cache invalidation
def invalidate_customer_cache(customer_id):
    cache_key = f"customer_data_{customer_id}"
    frappe.cache().delete(cache_key)

# In controller
class Customer(Document):
    def on_update(self):
        # Invalidate cache when customer is updated
        invalidate_customer_cache(self.name)
```

## 🛠️ Practical Exercises

### Exercise 6.1: ORM Methods Comparison

Compare performance of different ORM methods:
- `frappe.get_all()` vs `frappe.db.get_all()`
- Individual inserts vs bulk inserts
- With and without caching

### Exercise 6.2: Complex Query Writing

Write complex queries with:
- Multiple joins
- Subqueries
- Aggregations and grouping
- Performance optimization

### Exercise 6.3: Transaction Management

Implement transactions with:
- Savepoints
- Error handling
- Rollback scenarios
- Nested transactions

## 🚀 Best Practices

### Query Optimization

- **Use specific fields** instead of SELECT *
- **Add appropriate indexes** for frequently queried fields
- **Use LIMIT** for large result sets
- **Cache frequently accessed data**
- **Analyze slow queries** with EXPLAIN

### Transaction Management

- **Keep transactions short** to avoid locking
- **Use savepoints** for complex operations
- **Always handle errors** with rollback
- **Avoid nested transactions** when possible

### Performance Considerations

- **Use bulk operations** for multiple records
- **Batch processing** for large datasets
- **Optimize database connections**
- **Monitor query performance**

## 📖 Further Reading

- [Frappe Database API](https://frappeframework.com/docs/user/en/api/database)
- [MySQL Performance Optimization](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- [Database Indexing Guide](https://frappeframework.com/docs/user/en/development/database#indexing)

## 🎯 Chapter Summary

Mastering the Frappe ORM is essential for efficient database operations:

- **Document operations** provide intuitive data manipulation
- **Query methods** offer flexibility with different performance characteristics
- **Bulk operations** significantly improve performance for multiple records
- **Transaction management** ensures data integrity
- **Query optimization** maintains application performance

---

**Next Chapter**: Client-side mastery with JavaScript and form scripting.
