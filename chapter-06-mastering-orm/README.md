# Chapter 6: Mastering the Frappe ORM

## 🎯 Learning Objectives

By the end of this chapter, you will master:

- **How** the Frappe ORM internally manages database connections and query optimization
- **Why** different query methods have specific performance characteristics
- **When** to use raw SQL vs ORM methods for optimal performance
- **How** database transactions work within the ORM layer
- **Advanced patterns** for bulk operations and batch processing
- **Performance optimization** techniques for high-volume data operations

## 📚 Chapter Topics

### 6.1 Understanding the Frappe ORM Architecture

**The ORM Internal Structure**

The Frappe ORM is more than just a database abstraction layer—it's a sophisticated system that manages connections, optimizes queries, and provides intelligent caching mechanisms. Understanding its internal architecture is crucial for building high-performance applications.

#### How the ORM Manages Database Connections

```python
# Simplified version of Frappe's database connection manager
class DatabaseConnectionManager:
    """Manages database connections and connection pooling"""
    
    def __init__(self):
        self._connection_pool = []
        self._active_connections = {}
        self._connection_config = {}
        self._query_cache = {}
        self._performance_metrics = {}
        
        # Initialize connection pool
        self.initialize_connection_pool()
    
    def initialize_connection_pool(self):
        """Initialize database connection pool"""
        # Get database configuration
        db_config = frappe.conf.db_config
        
        # Create connection pool
        pool_size = db_config.get('max_connections', 10)
        
        for i in range(pool_size):
            try:
                connection = self.create_connection()
                self._connection_pool.append(connection)
                self._active_connections[connection.id] = connection
            except Exception as e:
                frappe.log_error(f"Failed to create connection {i+1}: {str(e)}")
    
    def create_connection(self):
        """Create a single database connection"""
        import pymysql
        
        connection = pymysql.connect(
            host=frappe.conf.db_host,
            port=frappe.conf.db_port,
            user=frappe.conf.db_user,
            password=frappe.db_password,
            database=frappe.conf.db_name,
            charset='utf8mb4',
            cursorclass=frappe.db.cursor_class,
            autocommit=False,
            connect_timeout=30,
            read_timeout=30
        )
        
        # Configure connection for performance
        connection.autocommit = False
        connection.query("SET SESSION sql_mode = 'STRICT_TRANS_TABLES'")
        connection.query("SET SESSION innodb_lock_wait_timeout = 60")
        
        return connection
    
    def get_connection(self, for_write=False):
        """Get connection from pool"""
        # Try to get existing connection
        for connection in self._connection_pool:
            if not connection.in_use and connection.is_connected():
                connection.in_use = True
                return connection
        
        # Create new connection if pool is exhausted
        if len(self._connection_pool) < 10:
            connection = self.create_connection()
            connection.in_use = True
            self._connection_pool.append(connection)
            self._active_connections[connection.id] = connection
            return connection
        
        # Wait for connection to become available
        raise Exception("Connection pool exhausted")
    
    def release_connection(self, connection):
        """Release connection back to pool"""
        if connection.id in self._active_connections:
            connection.in_use = False
    
    def execute_query(self, query, values=None, as_dict=False):
        """Execute query with connection management"""
        start_time = time.time()
        
        connection = self.get_connection()
        
        try:
            cursor = connection.cursor(pymysql.cursors.DictCursor if as_dict else pymysql.cursors.Cursor)
            
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            
            result = cursor.fetchall()
            
            # Track performance
            execution_time = time.time() - start_time
            self.track_query_performance(query, execution_time)
            
            return result
            
        except Exception as e:
            self.log_query_error(query, e)
            raise
        finally:
            self.release_connection(connection)
    
    def track_query_performance(self, query, execution_time):
        """Track query performance metrics"""
        query_hash = hash(query)
        
        if query_hash not in self._query_cache:
            self._query_cache[query_hash] = {
                'query': query,
                'execution_count': 0,
                'total_time': 0,
                'avg_time': 0,
                'max_time': 0,
                'min_time': float('inf')
            }
        
        metrics = self._query_cache[query_hash]
        metrics['execution_count'] += 1
        metrics['total_time'] += execution_time
        metrics['avg_time'] = metrics['total_time'] / metrics['execution_count']
        metrics['max_time'] = max(metrics['max_time'], execution_time)
        metrics['min_time'] = min(metrics['min_time'], execution_time)
        
        # Log slow queries
        if execution_time > 1.0:  # 1 second threshold
            frappe.logger.warning(f"Slow query detected: {query[:100]}... took {execution_time:.3f}s")
```

#### Query Builder Architecture

```python
# Frappe's query builder system
class QueryBuilder:
    """Builds and optimizes database queries"""
    
    def __init__(self, doctype):
        self.doctype = doctype
        self.table_name = f"tab{doctype}"
        self._fields = []
        self._filters = []
       ._joins = []
       ._group_by = []
       ._order_by = []
        self._limit = None
        _offset = None
    
    def select(self, fields=None):
        """Set fields for SELECT clause"""
        if fields:
            if isinstance(fields, str):
                self._fields = [fields.strip()]
            elif isinstance(fields, list):
                self._fields = fields
        return self
    
    def where(self, conditions):
        """Add WHERE conditions"""
        if conditions:
            if isinstance(conditions, dict):
                self._filters.append(conditions)
            elif isinstance(conditions, list):
                self._filters.extend(conditions)
        return self
    
    def join(self, table, on_clause, join_type="INNER JOIN"):
        """Add JOIN clause"""
        self._joins.append({
            'table': table,
            'on': on_clause,
            'type': join_type
        })
        return self
    
    def group_by(self, fields):
        """Add GROUP BY clause"""
        if fields:
            if isinstance(fields, str):
                self._group_by = [fields.strip()]
            elif isinstance(fields, list):
                self._group_by = fields
        return self
    
    def order_by(self, fields, order="ASC"):
        """Add ORDER BY clause"""
        if fields:
            if isinstance(fields, str):
                self._order_by = [(fields.strip(), order)]
            elif isinstance(fields, list):
                if isinstance(fields[0], tuple):
                    self._order_by = fields
                else:
                    self._order_by = [(field.strip(), order) for field in fields]
        return self
    
    def limit(self, limit, offset=None):
        """Add LIMIT clause"""
        self._limit = limit
        self._offset = offset
        return self
    
    def build(self):
        """Build the final SQL query"""
        query_parts = []
        
        # SELECT clause
        if self._fields:
            query_parts.append(f"SELECT {', '.join(self._fields)}")
        else:
            query_parts.append(f"SELECT *")
        
        # FROM clause
        query_parts.append(f"FROM {self.table_name}")
        
        # JOIN clauses
        for join in self._joins:
            query_parts.append(f"{join['type']} {join['table']} ON {join['on']}")
        
        # WHERE clause
        if self._filters:
            where_conditions = []
            for condition in self._filters:
                if isinstance(condition, dict):
                    for field, value in condition.items():
                        if isinstance(value, list):
                            where_conditions.append(f"{field} IN ({','.join([f"'{v}'" for v in value])})")
                        else:
                            where_conditions.append(f"{field} = '{value}'")
                elif isinstance(condition, list):
                    where_conditions.extend(condition)
            query_parts.append(f"WHERE {' AND '.join(where_conditions)}")
        
        # GROUP BY clause
        if self._group_by:
            query_parts.append(f"GROUP BY {', '.join(self._group_by)}")
        
        # ORDER BY clause
        if self._order_by:
            order_clauses = []
            for field, direction in self._order_by:
                order_clauses.append(f"{field} {direction}")
            query_parts.append(f"ORDER BY {', '.join(order_clauses)}")
        
        # LIMIT clause
        if self._limit:
            query_parts.append(f"LIMIT {self._limit}")
            if self._offset:
                query_parts.append(f"OFFSET {self._offset}")
        
        return ' '.join(query_parts)
    
    def execute(self, as_dict=True):
        """Execute the built query"""
        query = self.build()
        
        # For SELECT queries, use frappe.db.sql
        if query.startswith('SELECT'):
            return frappe.db.sql(query, as_dict=as_dict)
        else:
            # For other queries, use frappe.db.sql
            return frappe.db.sql(query)
```

#### Performance Monitoring and Analysis

```python
# Performance monitoring system for the ORM
class ORMPerformanceMonitor:
    """Monitors ORM performance and provides optimization recommendations"""
    
    def __init__(self):
        self._query_stats = {}
        self._slow_queries = []
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'hit_rate': 0
        }
        self._connection_stats = {
            'created': 0,
            'reused': 0,
            'closed': 0
        }
    
    def track_query(self, query, execution_time, result_count):
        """Track query execution metrics"""
        query_hash = hash(query)
        
        if query_hash not in self._query_stats:
            self._query_stats[query_hash] = {
                'query': query,
                'execution_count': 0,
                'total_time': 0,
                'avg_time': 0,
                'max_time': 0,
                'min_time': float('inf'),
                'result_count': 0
            }
        
        stats = self._query_stats[query_hash]
        stats['execution_count'] += 1
        stats['total_time'] += execution_time
        stats['avg_time'] = stats['total_time'] / stats['execution_count']
        stats['max_time'] = max(stats['max_time'], execution_time)
        stats['min_time'] = min(stats['min_time'], execution_time)
        stats['result_count'] += result_count
        
        # Track slow queries
        if execution_time > 1.0:
            self._slow_queries.append({
                'query': query,
                'execution_time': execution_time,
                'timestamp': frappe.utils.now()
            })
        
        # Log slow queries periodically
        if len(self._slow_queries) > 100:
            self.log_slow_queries()
    
    def log_slow_queries(self):
        """Log slow queries for optimization"""
        frappe.logger.warning("=== Slow Queries Detected ===")
        
        for query_info in self._slow_queries[-50:]:  # Last 50 slow queries
            frappe.logger.warning(
                f"Query: {query_info['query'][:100]}... "
                f"Time: {query_info['execution_time']:.3f}s "
                f"Date: {query_info['timestamp']}"
            )
        
        self._slow_queries = []
    
    def analyze_query_patterns(self):
        """Analyze query patterns for optimization opportunities"""
        query_patterns = {}
        
        for query_hash, stats in self._query_stats.items():
            # Categorize queries by table
            if 'FROM' in stats['query']:
                table_name = stats['query'].split('FROM ')[1].split()[0]
                
                if table_name not in query_patterns:
                    query_patterns[table_name] = {
                        'total_queries': 0,
                        'total_time': 0,
                        'avg_time': 0,
                        'slow_queries': 0
                    }
                
                patterns = query_patterns[table_name]
                patterns['total_queries'] += stats['execution_count']
                patterns['total_time'] += stats['total_time']
                patterns['avg_time'] = patterns['total_time'] / patterns['total_queries']
                patterns['slow_queries'] += 1 if stats['avg_time'] > 1.0 else 0
        
        # Generate recommendations
        recommendations = []
        
        for table_name, patterns in query_patterns.items():
            if patterns['avg_time'] > 0.5:
                recommendations.append(
                    f"Consider optimizing queries for table {table_name}. "
                    f"Average time: {patterns['avg_time']:.3f}s"
                )
            
            if patterns['slow_queries'] > 10:
                recommendations.append(
                    f"High number of slow queries for table {table_name}. "
                    f"Consider adding indexes or optimizing queries."
                )
        
        return recommendations
    
    def get_performance_report(self):
        """Get comprehensive performance report"""
        return {
            'query_stats': {
                'total_queries': sum(stats['execution_count'] for stats in self._query_stats.values()),
                'total_time': sum(stats['total_time'] for stats in self._query_stats.values()),
                'avg_time': sum(stats['total_time'] for stats in self._query_stats.values()) / sum(stats['execution_count'] for stats in self._query_stats.values()),
                'slow_queries': len(self._slow_queries)
            },
            'cache_stats': self._cache_stats,
            'connection_stats': self._connection_stats,
            'recommendations': self.analyze_query_patterns()
        }
```

### 6.2 Advanced Document Operations with Performance Optimization

#### Document Loading Strategies

```python
# Performance-optimized document loading
class OptimizedDocumentLoader:
    """Optimized document loading with caching and batch operations"""
    
    def __init__(self):
        self._document_cache = {}
        self._batch_load_queue = []
        self._cache_ttl = 300  # 5 minutes
    
    def get_document_optimized(self, doctype, name, fields=None):
        """Get document with intelligent caching"""
        cache_key = f"doc_{doctype}_{name}"
        
        # Check cache first
        cached_doc = self._document_cache.get(cache_key)
        if cached_doc:
            # Check if cache is still valid
            cache_age = time.time() - cached_doc['timestamp']
            if cache_age < self._cache_ttl:
                return cached_doc['document']
        
        # Load from database
        doc = frappe.get_doc(doctype, name, fields)
        
        # Cache the document
        self._document_cache[cache_key] = {
            'document': doc,
            'timestamp': time.time()
        }
        
        return doc
    
    def batch_load_documents(self, doctype, names, fields=None):
        """Batch load multiple documents efficiently"""
        if not names:
            return []
        
        # Build query for batch loading
        table_name = f"tab{doctype}"
        field_list = fields or ['*']
        
        # Build WHERE clause (SECURE: Using parameterized query)
        placeholders = ', '.join(['%s'] * len(names))
        where_clause = f"name IN ({placeholders})"
        
        # Execute batch query (SECURE: Using parameterized query)
        documents = frappe.db.sql(f"""
            SELECT {', '.join(field_list)}
            FROM {table_name}
            WHERE {where_clause}
        """, tuple(names), as_dict=True)
        
        # Cache each document
        for doc_data in documents:
            cache_key = f"doc_{doctype}_{doc_data['name']}"
            self._document_cache[cache_key] = {
                'document': frappe.get_doc(doctype, doc_data['name'], fields),
                'timestamp': time.time()
            }
        
        return documents
    
    def preload_related_documents(self, doctype, related_doctypes, parent_name):
        """Preload related documents for better performance"""
        cache_key = f"related_{doctype}_{parent_name}"
        
        # Check cache first
        cached_data = self._document_cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Get related documents
        related_data = {}
        
        for related_doctype in related_doctypes:
            # Get all documents of related doctype
            related_docs = frappe.get_all(related_doctype, 
                                        filters={'parent': parent_name},
                                        fields=['name', 'modified'])
            
            related_data[related_doctype] = {doc['name']: doc for doc in related_docs}
        
        # Cache the related data
        self._document_cache[cache_key] = {
            'related_data': related_data,
            'timestamp': time.time()
        }
        
        return related_data
```

#### Document Creation Patterns

```python
# High-performance document creation
class OptimizedDocumentCreator:
    """Optimized document creation with batch operations"""
    
    def __init__(self):
        self._batch_queue = []
        self._batch_size = 100
        self._pending_creations = []
    
    def create_document_batch(self, doctype, documents_data):
        """Create multiple documents in batch"""
        if not documents_data:
            return []
        
        # Prepare batch data
        batch_data = []
        for doc_data in documents_data:
            # Ensure required fields
            if not doc_data.get('doctype'):
                doc_data['doctype'] = doctype
            
            # Add standard fields
            doc_data.update({
                'creation': frappe.utils.now(),
                'modified': frappe.utils.now(),
                'owner': frappe.session.user,
                'modified_by': frappe.session.user,
                'docstatus': 0
            })
            
            batch_data.append(doc_data)
        
        # Use bulk insert for performance
        try:
            frappe.db.bulk_insert(doctype, batch_data)
            return [doc['name'] for doc in batch_data]
        except Exception as e:
            frappe.log_error(f"Bulk insert failed: {str(e)}")
            # Fall back to individual inserts
            return self.create_documents_individually(doctype, documents_data)
    
    def create_documents_individually(self, doctype, documents_data):
        """Create documents individually (fallback method)"""
        created_names = []
        
        for doc_data in documents_data:
            try:
                doc = frappe.get_doc(doc_data)
                doc.insert()
                created_names.append(doc.name)
            except Exception as e:
                frappe.log_error(f"Failed to create document: {str(e)}")
        
        return created_names
    
    def create_document_with_transaction(self, doctype, doc_data):
        """Create document with transaction support"""
        frappe.db.begin()
        
        try:
            doc = frappe.get_doc(doc_data)
            doc.insert()
            frappe.db.commit()
            return doc.name
        except Exception as e:
            frappe.db.rollback()
            raise e
    
    def create_document_with_validation(self, doctype, doc_data, validation_func=None):
        """Create document with custom validation"""
        if validation_func:
            # Pre-validation
            if not validation_func(doc_data):
                raise Exception("Pre-validation failed")
        
        return self.create_document_with_transaction(doctype, doc_data)
```

#### Document Update Optimization

```python
# Optimized document updating
class OptimizedDocumentUpdater:
    """Optimized document updating with change tracking"""
    
    def __init__(self):
        self._update_queue = []
        self._batch_updates = {}
    
    def update_document_optimized(self, doc, field_dict):
        """Update document with change tracking"""
        # Track changes
        changes = []
        
        for field, value in field_dict.items():
            if doc.get(field) != value:
                changes.append(field)
        
        if not changes:
            return False  # No changes
        
        # Use direct SQL for single field updates
        if len(changes) == 1:
            field, value = changes[0]
            frappe.db.set_value(doc.doctype, doc.name, field, value)
        else:
            # Multiple field updates
            self._batch_updates[doc.name] = field_dict
        
        return True
    
    def batch_update_documents(self, updates):
        """Batch update multiple documents"""
        if not updates:
            return []
        
        updated_names = []
        
        for doc_name, field_dict in updates.items():
            try:
                doc = frappe.get_doc('Customer', doc_name)
                
                # Update fields
                for field, value in field_dict.items():
                    doc.set(field, value)
                
                doc.save()
                updated_names.append(doc_name)
                
            except Exception as e:
                frappe.log_error(f"Failed to update document {doc_name}: {str(e)}")
        
        return updated_names
    
    def smart_update_document(self, doc, field_dict):
        """Smart document update with validation"""
        # Validate before update
        self.validate_update_data(doc, field_dict)
        
        # Check for conflicts
        if self.has_update_conflicts(doc, field_dict):
            frappe.throw("Update conflict detected")
        
        # Perform update
        return self.update_document_optimized(doc, field_dict)
    
    def validate_update_data(self, doc, field_dict):
        """Validate data before update"""
        # Check data types
        for field, value in field_dict.items():
            field_meta = doc.meta.get_field(field)
            if field_meta:
                self.validate_field_value(field, value, field_meta)
        
        # Check business rules
        self.validate_business_rules(doc, field_dict)
    
    def validate_field_value(self, field, value, field_meta):
        """Validate individual field value"""
        fieldtype = field_meta.get('fieldtype')
        
        if fieldtype == 'Email':
            if not frappe.utils.validate_email(value):
                frappe.throw(f"Invalid email format: {value}")
        elif fieldtype == 'Date':
            try:
                frappe.utils.getdate(value)
            except:
                frappe.throw(f"Invalid date format: {value}")
        elif fieldtype == 'Currency':
            try:
                flt(value)
            except:
                frappe.frappe.throw(f"Invalid currency format: {value}")
        elif fieldtype == 'Link':
            if value and not frappe.db.exists(field_meta.get('options'), value):
                frappe.throw(f"Invalid reference: {value}")
    
    def validate_business_rules(self, doc, field_dict):
        """Validate business rules"""
        # Example: Don't allow negative amounts
        if field_dict.get('amount') and field_dict['amount'] < 0:
            frappe.throw("Amount cannot be negative")
        
        # Example: Check date ranges
        if 'start_date' in field_dict and 'end_date' in field_dict:
            start_date = frappe.utils.getdate(field_dict['start_date'])
            end_date = frappe.getdate(field_dict['end_date'])
            if start_date > end_date:
                frappe("Start date cannot be after end date")
    
    def has_update_conflicts(self, doc, field_dict):
        """Check for update conflicts"""
        for field, value in field_dict.items():
            if hasattr(doc, field) and doc.get(field) != value:
                # Check if another user modified the same field
                if doc._original_data.get(field) and doc._original_data[field] != value:
                    return True
        return False
```

#### Document Deletion and Archival

```python
# Optimized document deletion
class OptimizedDocumentDeleter:
    """Optimized document deletion with cascade handling"""
    
    def __init__(self):
        self._delete_queue = []
        self._batch_deletes = []
    
    def delete_document_optimized(self, doctype, name):
        """Delete document with cascade handling"""
        try:
            # Check for dependencies
            dependencies = self.get_document_dependencies(doctype, name)
            
            # Archive document first
            self.archive_document(doctype, name)
            
            # Delete related records
            self.delete_related_records(doctype, name)
            
            # Delete the document
            frappe.delete_doc(doctype, name)
            
        except Exception as e:
            frappe.log_error(f"Failed to delete document {doctype} {name}: {str(e)}")
            raise
    
    def delete_documents_batch(self, doctype, names):
        """Delete multiple documents efficiently"""
        if not names:
            return []
        
        deleted_names = []
        
        for name in names:
            try:
                self.delete_document_optimized(doctype, name)
                deleted_names.append(name)
            except Exception as e:
                frappe.log_error(f"Failed to delete document {name}: {str(e)}")
        
        return deleted_names
    
    def archive_document(self, doctype, name):
        """Archive document before deletion"""
        # Create archive record
        archive_doc = frappe.get_doc({
            'doctype': 'Archived Document',
            'archived_doctype': doctype,
            'archived_name': name,
            'archived_data': frappe.get_doc(doctype, name).as_dict(),
            'archived_by': frappe.session.user,
            'archived_on': frappe.utils.now()
        })
        archive_doc.insert()
    
    def get_document_dependencies(self, doctype, name):
        """Get all documents that depend on this document"""
        dependencies = []
        
        # Check child tables
        child_tables = frappe.get_meta(doctype).get('child_tables', [])
        for child_table in child_tables:
            child_docs = frappe.get_all(child_table, filters={'parent': name})
            dependencies.extend([f"{child_table}:{doc.name}" for doc in child_docs])
        
        # Check Link fields
        link_fields = frappe.get_meta(doctype).get('link_fields', [])
        for field in link_fields:
            if hasattr(frappe.db, 'exists'):
                linked_docs = frappe.db.sql(f"""
                    SELECT name FROM `tab{field.options}` 
                    WHERE name = (SELECT name FROM `tab{doctype}` WHERE name = %s)
                """, (name,), as_dict=True)
                dependencies.extend([f"{field.options}:{doc.name}" for doc in linked_docs])
        
        return dependencies
```

#### Document Serialization and Export

```python
# Optimized document serialization
class OptimizedDocumentSerializer:
    """Optimized document serialization with caching"""
    
    def __init__(self):
        self._serialization_cache = {}
        self._export_cache = {}
    
    def serialize_document(self, doc, include_children=False):
        """Serialize document with optional child tables"""
        cache_key = f"serialize_{doc.doctype}_{doc.name}"
        
        # Check cache first
        cached_data = self._serialization_cache.get(cache_key)
        if cached_data:
            cache_age = time.time() - cached_data['timestamp']
            if cache_age < 60:  # 1 minute cache
                return cached_data['data']
        
        # Build document data
        doc_data = doc.as_dict()
        
        if include_children:
            # Add child tables
            child_tables = frappe.get_meta(doc.doctype).get('child_tables', [])
            for child_table in child_tables:
                child_data = []
                child_docs = frappe.get_all(child_table, filters={'parent': doc.name}, as_dict=True)
                child_data.extend([doc.as_dict() for doc in child_docs])
                doc_data[child_table] = child_data
        
        # Cache the serialized data
        self._serialization_cache[cache_key] = {
            'data': doc_data,
            'timestamp': time.time()
        }
        
        return doc_data
    
    def export_document(self, doc, format='json', include_children=False):
        """Export document in specified format"""
        if format == 'json':
            return json.dumps(self.serialize_document(doc, include_children), indent=2)
        elif format == 'csv':
            return self.export_to_csv(doc, include_children)
        elif format == 'xml':
            return self.export_to_xml(doc, include_children)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_to_csv(self, doc, include_children=False):
        """Export document to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        
        if include_children:
            # Export parent document
            writer = csv.DictWriter(output, fieldnames=doc.keys())
            writer.writeheader()
            writer.writerow(doc.as_dict())
            
            # Export child tables
            child_tables = frappe.get_meta(doc.doctype).get('child_tables', [])
            for child_table in child_tables:
                child_docs = frappe.get_all(child_table, filters={'parent': doc.name}, as_dict=True)
                for child_doc in child_docs:
                    writer.writerow(child_doc.as_dict())
        else:
            # Export only parent document
            writer = csv.DictWriter(output, fieldnames=doc.keys())
            writer.writeheader()
            writer.writerow(doc.as_dict())
        
        return output.getvalue()
    
    def export_to_xml(self, doc, include_children=False):
        """Export document to XML format"""
        import xml.etree.Element as ET
        
        # Create root element
        root = ET.Element(doc.doctype)
        
        # Add document fields
        for field in doc.meta.get('fields', []):
            field_element = ET.SubElement(root, field.fieldname)
            field_element.text = str(doc.get(field.fieldname))
        
        if include_children:
            # Add child tables
            child_tables = frappe.get_meta(doc.doctype).get('child_tables', [])
            for child_table in child_tables:
                child_element = ET.SubElement(root, child_table)
                
                # Add child documents
                child_docs = frappe.get_all(child_table, filters={'parent': doc.name}, as_dict=True)
                for child_doc in child_docs:
                    child_element = ET.SubElement(child_element, child_doc.doctype)
                    for field in child_doc.meta.get('fields', []):
                        field_element = ET.SubElement(child_element, field.fieldname)
                        field_element.text = str(child_doc.get(field.fieldname))
        
        return ET.tostring(root, encoding='unicode')

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


---

## 📌 Addendum: Choosing the Right ORM Method — N+1 Implications

### frappe.db.get_value vs frappe.db.get_all vs frappe.get_doc

| Method | Returns | Best for | Watch out for |
|--------|---------|----------|---------------|
| `frappe.db.get_value(doctype, name, fieldname)` | Single scalar or tuple | One field / a few fields from one known document | Returns `None` silently if doc doesn't exist |
| `frappe.db.get_all(doctype, filters, fields)` | List of dicts | Filtered lists, reports, dashboards | Does **not** load child tables; respects permissions |
| `frappe.get_doc(doctype, name)` | Full Document object | When you need to call methods, access child tables, or run hooks | Loads **all** fields + child tables — expensive in loops |

### The N+1 Problem in Frappe

The classic N+1 pattern looks like this:

```python
# ❌ BAD — 1 query to get orders + N queries inside the loop
orders = frappe.get_all('Sales Order', filters={'docstatus': 1}, fields=['name', 'customer'])
for order in orders:
    # This fires a separate SQL query for EVERY order
    credit_limit = frappe.db.get_value('Customer', order.customer, 'credit_limit')
    process(order, credit_limit)
```

Fix it with a single batch query:

```python
# ✅ GOOD — 2 queries total regardless of list size
orders = frappe.get_all('Sales Order', filters={'docstatus': 1}, fields=['name', 'customer'])

# Collect unique customers, fetch all at once
customer_names = list({o.customer for o in orders})
customers = frappe.get_all(
    'Customer',
    filters={'name': ['in', customer_names]},
    fields=['name', 'credit_limit']
)
credit_map = {c.name: c.credit_limit for c in customers}

for order in orders:
    process(order, credit_map.get(order.customer, 0))
```

### When to use each

```python
# frappe.db.get_value — single field lookup
email = frappe.db.get_value('Customer', 'CUST-001', 'email_id')

# frappe.db.get_value — multiple fields (returns tuple)
name, group = frappe.db.get_value('Customer', 'CUST-001', ['customer_name', 'customer_group'])

# frappe.db.get_all — filtered list (no child tables)
active_customers = frappe.db.get_all(
    'Customer',
    filters={'status': 'Active'},
    fields=['name', 'customer_name', 'credit_limit'],
    order_by='customer_name asc',
    limit=100
)

# frappe.get_doc — full document with child tables and method access
so = frappe.get_doc('Sales Order', 'SO-0001')
so.submit()  # calls on_submit hooks, updates docstatus, etc.

# frappe.db.sql — complex aggregations the ORM cannot express
result = frappe.db.sql("""
    SELECT customer, SUM(grand_total) as total
    FROM `tabSales Order`
    WHERE docstatus = 1
    GROUP BY customer
    HAVING total > 50000
    ORDER BY total DESC
""", as_dict=True)
```
