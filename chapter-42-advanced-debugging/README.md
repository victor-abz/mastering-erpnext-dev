# Chapter 42: Advanced Debugging - Mastering Troubleshooting and Performance Analysis

## 🎯 Learning Objectives

By the end of this chapter, you will master:
- **Using** advanced debugging tools and techniques for ERPNext
- **Analyzing** performance bottlenecks with profiling tools
- **Debugging** complex Frappe framework internals
- **Implementing** comprehensive logging and monitoring
- **Troubleshooting** production issues systematically
- **Using** browser developer tools for client-side debugging
- **Analyzing** database queries and optimization
- **Setting up** debugging environments for complex scenarios

## 📚 Chapter Topics

### 42.1 Understanding ERPNext Debugging Architecture

**Debugging Framework Overview**

ERPNext provides multiple layers of debugging capabilities, from basic logging to advanced profiling. Understanding this architecture is crucial for effective troubleshooting.

> **📊 Visual Reference**: See performance optimization architecture in `resources/diagrams/performance_optimization.md` for understanding how debugging fits into overall system monitoring.

#### Debugging Layers

```python
# ERPNext debugging architecture
class ERPNextDebuggingArchitecture:
    """Comprehensive debugging architecture for ERPNext"""
    
    DEBUGGING_LAYERS = {
        'application_logging': {
            'level': 'Basic',
            'tools': ['frappe.log()', 'frappe.log_error()', 'Custom logging'],
            'scope': 'Application events, errors, business logic',
            'output': 'Log files, console output'
        },
        'framework_debugging': {
            'level': 'Intermediate',
            'tools': ['frappe.debug()', 'Developer tools', 'Traceback analysis'],
            'scope': 'Framework internals, ORM operations, hooks',
            'output': 'Debug console, log files'
        },
        'database_debugging': {
            'level': 'Advanced',
            'tools': ['EXPLAIN analysis', 'Slow query log', 'Connection monitoring'],
            'scope': 'SQL queries, database performance, deadlocks'],
            'output': 'Query logs, performance metrics'
        },
        'performance_profiling': {
            'level': 'Advanced',
            'tools': ['cProfile', 'Memory profiling', 'Request timing'],
            'scope': 'Code execution, memory usage, request lifecycle'],
            'output': 'Profile reports, flame graphs'
        },
        'production_monitoring': {
            'level': 'Production',
            'tools': ['APM tools', 'Error tracking', 'Performance monitoring'],
            'scope': 'Production issues, user experience, system health'],
            'output': 'Monitoring dashboards, alerts'
        }
    }
    
    def get_debugging_strategy(self, environment, issue_type):
        """Get appropriate debugging strategy for environment and issue type"""
        
        strategies = {
            'development': {
                'logic_errors': ['framework_debugging', 'application_logging'],
                'performance_issues': ['performance_profiling', 'database_debugging'],
                'integration_issues': ['framework_debugging', 'network_debugging']
            },
            'staging': {
                'logic_errors': ['framework_debugging', 'application_logging'],
                'performance_issues': ['performance_profiling', 'database_debugging'],
                'integration_issues': ['framework_debugging', 'network_debugging']
            },
            'production': {
                'logic_errors': ['application_logging', 'production_monitoring'],
                'performance_issues': ['production_monitoring', 'database_debugging'],
                'integration_issues': ['production_monitoring', 'network_debugging']
            }
        }
        
        return strategies.get(environment, {}).get(issue_type, ['application_logging'])
```

### 42.2 Advanced Logging and Monitoring

**Comprehensive Logging Framework**

```python
# Advanced logging framework
class AdvancedLoggingFramework:
    """Advanced logging framework for ERPNext applications"""
    
    def __init__(self):
        self.log_levels = {
            'DEBUG': 10,
            'INFO': 20,
            'WARNING': 30,
            'ERROR': 40,
            'CRITICAL': 50
        }
        self.log_categories = {
            'APP': 'Application Logic',
            'DB': 'Database Operations',
            'API': 'API Calls',
            'PERF': 'Performance',
            'SEC': 'Security',
            'INT': 'Integrations'
        }
        self.log_handlers = []
        self.setup_log_handlers()
    
    def setup_log_handlers(self):
        """Setup different log handlers"""
        
        # File handler for persistent logging
        file_handler = {
            'type': 'file',
            'path': 'logs/erpnext_{date}.log',
            'rotation': 'daily',
            'max_size': '100MB',
            'backup_count': 30
        }
        
        # Database handler for structured logging
        db_handler = {
            'type': 'database',
            'table': 'Application Log',
            'fields': ['timestamp', 'level', 'category', 'message', 'context', 'user'],
            'indexes': ['timestamp', 'level', 'category']
        }
        
        # External monitoring handler
        external_handler = {
            'type': 'external',
            'service': 'Sentry/ELK Stack',
            'api_endpoint': 'https://logs.yourcompany.com/api/logs',
            'batch_size': 100,
            'flush_interval': 60  # seconds
        }
        
        self.log_handlers = [file_handler, db_handler, external_handler]
    
    def log_structured(self, level, category, message, context=None, user=None):
        """Log structured message with context"""
        
        log_entry = {
            'timestamp': frappe.utils.now(),
            'level': level,
            'level_name': self._get_level_name(level),
            'category': category,
            'category_name': self.log_categories.get(category, category),
            'message': message,
            'context': context or {},
            'user': user or frappe.session.user,
            'request_id': getattr(frappe.local, 'request_id', None),
            'session_id': frappe.session.sid if frappe.session else None
        }
        
        # Add performance context if available
        if hasattr(frappe.local, 'request_start'):
            log_entry['duration'] = (
                frappe.utils.now() - frappe.local.request_start
            ).total_seconds()
        
        # Send to all handlers
        for handler in self.log_handlers:
            self._send_to_handler(handler, log_entry)
    
    def log_performance(self, operation, duration, details=None):
        """Log performance metrics"""
        
        perf_entry = {
            'timestamp': frappe.utils.now(),
            'operation': operation,
            'duration_ms': duration * 1000,
            'details': details or {},
            'user': frappe.session.user,
            'request_id': getattr(frappe.local, 'request_id', None)
        }
        
        # Check performance thresholds
        thresholds = self._get_performance_thresholds()
        if operation in thresholds and duration > thresholds[operation]:
            self.log_structured(
                self.log_levels['WARNING'],
                'PERF',
                f"Performance threshold exceeded for {operation}",
                {
                    'duration': duration,
                    'threshold': thresholds[operation],
                    'details': details
                }
            )
        
        # Log performance data
        self._send_to_handler(self.log_handlers[1], perf_entry)  # Database handler
    
    def log_api_call(self, method, endpoint, params, response, duration, status_code):
        """Log API call details"""
        
        api_entry = {
            'timestamp': frappe.utils.now(),
            'method': method,
            'endpoint': endpoint,
            'params': self._sanitize_params(params),
            'response_size': len(str(response)) if response else 0,
            'duration_ms': duration * 1000,
            'status_code': status_code,
            'user': frappe.session.user,
            'ip_address': frappe.local.request_ip
        }
        
        # Log API errors
        if status_code >= 400:
            self.log_structured(
                self.log_levels['ERROR'],
                'API',
                f"API call failed: {method} {endpoint}",
                {
                    'status_code': status_code,
                    'response': response[:500] if response else None
                }
            )
        
        # Log API call
        self._send_to_handler(self.log_handlers[1], api_entry)
    
    def _get_performance_thresholds(self):
        """Get performance thresholds for different operations"""
        
        return {
            'database_query': 1.0,  # 1 second
            'api_request': 2.0,   # 2 seconds
            'file_upload': 5.0,    # 5 seconds
            'report_generation': 10.0,  # 10 seconds
            'data_sync': 30.0      # 30 seconds
        }
    
    def _sanitize_params(self, params):
        """Sanitize parameters for logging"""
        
        if not params:
            return {}
        
        sanitized = {}
        for key, value in params.items():
            if key.lower() in ['password', 'secret', 'token', 'key']:
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, str) and len(value) > 100:
                sanitized[key] = value[:100] + '...'
            else:
                sanitized[key] = value
        
        return sanitized
```

### 42.3 Database Debugging and Query Analysis

**Advanced Database Debugging**

```python
# Database debugging tools
class DatabaseDebugger:
    """Advanced database debugging and query analysis"""
    
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.connection_monitor = ConnectionMonitor()
        self.deadlock_detector = DeadlockDetector()
    
    def analyze_slow_queries(self, time_threshold=1.0):
        """Analyze slow queries in the system"""
        
        slow_queries = frappe.db.sql("""
            SELECT 
                query_time,
                lock_time,
                rows_sent,
                rows_examined,
                sql_text,
                digest_text
            FROM performance_schema.events_statements_summary 
            WHERE digest_text NOT LIKE '%SHOW%'
            AND query_time > %s
            ORDER BY query_time DESC
            LIMIT 50
        """, (time_threshold,), as_dict=True)
        
        analysis_results = []
        
        for query in slow_queries:
            analysis = {
                'query': query['sql_text'],
                'query_time': query['query_time'],
                'lock_time': query['lock_time'],
                'rows_sent': query['rows_sent'],
                'rows_examined': query['rows_examined'],
                'efficiency': query['rows_examined'] / query['rows_sent'] if query['rows_sent'] > 0 else 1,
                'issues': [],
                'recommendations': []
            }
            
            # Analyze query issues
            if analysis['efficiency'] > 1000:
                analysis['issues'].append('High rows examined ratio')
                analysis['recommendations'].append('Add appropriate indexes')
            
            if query['lock_time'] > query['query_time'] * 0.5:
                analysis['issues'].append('High lock time')
                analysis['recommendations'].append('Check for locking issues')
            
            # Check for full table scans
            if 'ALL' in query['sql_text'].upper():
                analysis['issues'].append('Full table scan detected')
                analysis['recommendations'].append('Add WHERE clause or indexes')
            
            # Check for missing indexes
            missing_indexes = self._check_missing_indexes(query['sql_text'])
            if missing_indexes:
                analysis['issues'].append(f"Missing indexes on: {', '.join(missing_indexes)}")
                analysis['recommendations'].append(f"Add indexes on: {', '.join(missing_indexes)}")
            
            analysis_results.append(analysis)
        
        return analysis_results
    
    def _check_missing_indexes(self, query):
        """Check for potential missing indexes in query"""
        
        # Simple heuristic for missing indexes
        missing_indexes = []
        
        # Look for WHERE clauses without indexes
        if 'WHERE' in query.upper():
            # Extract column names from WHERE clause
            where_clause = query.upper().split('WHERE')[1].split('ORDER BY')[0].split('GROUP BY')[0]
            
            # Common indexed columns that should be indexed
            indexed_columns = ['customer', 'date', 'status', 'item_code', 'transaction_date']
            
            for col in indexed_columns:
                if col.upper() in where_clause:
                    missing_indexes.append(col)
        
        return missing_indexes
    
    def monitor_database_connections(self):
        """Monitor database connection usage"""
        
        connection_stats = frappe.db.sql("""
            SELECT 
                THREAD_ID,
                USER,
                HOST,
                DB,
                COMMAND,
                TIME,
                STATE,
                INFO
            FROM INFORMATION_SCHEMA.PROCESSLIST
            WHERE COMMAND != 'Sleep'
            ORDER BY TIME DESC
        """, as_dict=True)
        
        analysis = {
            'total_connections': len(connection_stats),
            'active_queries': [conn for conn in connection_stats if conn['STATE'] == 'Query'],
            'long_running_queries': [conn for conn in connection_stats if conn['TIME'] > 30],
            'connection_by_user': {},
            'potential_issues': []
        }
        
        # Group connections by user
        for conn in connection_stats:
            user = conn['USER']
            if user not in analysis['connection_by_user']:
                analysis['connection_by_user'][user] = 0
            analysis['connection_by_user'][user] += 1
        
        # Check for connection issues
        if analysis['total_connections'] > 100:
            analysis['potential_issues'].append('High connection count')
        
        if len(analysis['long_running_queries']) > 5:
            analysis['potential_issues'].append('Multiple long-running queries')
        
        return analysis
    
    def detect_deadlocks(self):
        """Detect and analyze database deadlocks"""
        
        deadlock_info = frappe.db.sql("""
            SHOW ENGINE INNODB STATUS
        """, as_dict=True)
        
        deadlock_stats = {}
        
        for stat in deadlock_info:
            if 'Innodb_deadlocks' in stat['Variable_name']:
                deadlock_stats['total_deadlocks'] = int(stat['Value'])
            elif 'Innodb_lock_waits' in stat['Variable_name']:
                deadlock_stats['lock_waits'] = int(stat['Value'])
        
        # Get recent deadlock information
        recent_deadlocks = frappe.db.sql("""
            SELECT 
                r.trx_id waiting_trx_id,
                r.trx_mysql_thread_id waiting_thread,
                r.trx_query waiting_query,
                b.trx_id blocking_trx_id,
                b.trx_mysql_thread_id blocking_thread,
                b.trx_query blocking_query
            FROM information_schema.innodb_lock_waits w
            INNER JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id
            INNER JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id
            WHERE w.blocking_trx_id IS NOT NULL
            ORDER BY w.waiting_started
            LIMIT 10
        """, as_dict=True)
        
        deadlock_analysis = {
            'stats': deadlock_stats,
            'recent_deadlocks': recent_deadlocks,
            'recommendations': []
        }
        
        if deadlock_stats.get('total_deadlocks', 0) > 0:
            deadlock_analysis['recommendations'].append(
                'Review transaction isolation levels and query order'
            )
        
        return deadlock_analysis
```

### 42.4 Performance Profiling and Optimization

**Advanced Performance Profiling**

```python
# Performance profiling tools
class PerformanceProfiler:
    """Advanced performance profiling for ERPNext"""
    
    def __init__(self):
        self.profiler = None
        self.memory_profiler = None
        self.request_profiler = RequestProfiler()
        self.setup_profilers()
    
    def setup_profilers(self):
        """Setup different profiling tools"""
        
        try:
            import cProfile
            import pstats
            import io
            
            self.profiler = cProfile.Profile()
            self.stats_buffer = io.StringIO()
            
        except ImportError:
            frappe.log("cProfile not available")
        
        try:
            import memory_profiler
            self.memory_profiler = memory_profiler.Profile()
        except ImportError:
            frappe.log("memory_profiler not available")
    
    def profile_function(self, func, *args, **kwargs):
        """Profile a specific function"""
        
        if not self.profiler:
            return func(*args, **kwargs)
        
        # Enable profiling
        self.profiler.enable()
        
        try:
            result = func(*args, **kwargs)
        finally:
            # Disable profiling and get stats
            self.profiler.disable()
            
            # Create stats object
            import pstats
            stats = pstats.Stats(self.profiler, stream=self.stats_buffer)
            
            # Analyze results
            analysis = self._analyze_profile_stats(stats, func.__name__)
            
            # Log profiling results
            self.log_profiling_results(analysis)
        
        return result
    
    def profile_memory_usage(self, func, *args, **kwargs):
        """Profile memory usage of a function"""
        
        if not self.memory_profiler:
            return func(*args, **kwargs)
        
        # Enable memory profiling
        self.memory_profiler.enable()
        
        try:
            result = func(*args, **kwargs)
        finally:
            # Disable profiling and get results
            self.memory_profiler.disable()
            
            # Get memory stats
            memory_stats = self.memory_profiler.get_stats()
            
            # Analyze memory usage
            analysis = self._analyze_memory_stats(memory_stats, func.__name__)
            
            # Log memory results
            self.log_memory_results(analysis)
        
        return result
    
    def _analyze_profile_stats(self, stats, func_name):
        """Analyze cProfile statistics"""
        
        # Get top functions by time
        stats.sort_stats('cumulative')
        top_functions = stats.get_stats_profile().funcs[:20]
        
        analysis = {
            'function': func_name,
            'total_calls': stats.total_calls,
            'total_time': stats.total_tt,
            'primitive_calls': stats.prim_calls,
            'top_functions': [],
            'performance_issues': []
        }
        
        for func_info in top_functions:
            func_data = {
                'name': func_info[2],  # function name
                'calls': func_info[0],  # call count
                'total_time': func_info[3],  # cumulative time
                'per_call_time': func_info[3] / func_info[0],  # time per call
                'filename': func_info[1],  # filename
                'line_number': func_info[4]  # line number
            }
            analysis['top_functions'].append(func_data)
            
            # Check for performance issues
            if func_data['per_call_time'] > 1.0:  # > 1 second per call
                analysis['performance_issues'].append(
                    f"Slow function: {func_data['name']} ({func_data['per_call_time']:.3f}s)"
                )
        
        return analysis
    
    def _analyze_memory_stats(self, stats, func_name):
        """Analyze memory profiling statistics"""
        
        # Get memory usage by line
        memory_by_line = stats[0] if stats else {}
        
        total_memory = sum(
            stat[2] for stat in memory_by_line.values() 
            if isinstance(stat, tuple) and len(stat) > 2
        )
        
        analysis = {
            'function': func_name,
            'total_memory_mb': total_memory / (1024 * 1024),  # Convert to MB
            'peak_memory_mb': max(
                stat[2] / (1024 * 1024) 
                for stat in memory_by_line.values() 
                if isinstance(stat, tuple) and len(stat) > 2
            ) if memory_by_line else 0,
            'memory_hotspots': [],
            'memory_issues': []
        }
        
        # Find memory hotspots
        for line, stat in memory_by_line.items():
            if isinstance(stat, tuple) and len(stat) > 2:
                memory_mb = stat[2] / (1024 * 1024)
                if memory_mb > 10:  # > 10MB on single line
                    analysis['memory_hotspots'].append({
                        'line': line,
                        'memory_mb': memory_mb,
                        'code': stat[3] if len(stat) > 3 else 'Unknown'
                    })
        
        # Check for memory issues
        if analysis['peak_memory_mb'] > 100:  # > 100MB peak
            analysis['memory_issues'].append(
                f"High memory usage: {analysis['peak_memory_mb']:.1f}MB"
            )
        
        return analysis
    
    def log_profiling_results(self, analysis):
        """Log profiling results"""
        
        frappe.log_error(f"Performance Profile: {analysis['function']}", {
            'total_calls': analysis['total_calls'],
            'total_time': analysis['total_time'],
            'top_functions': analysis['top_functions'][:5],
            'performance_issues': analysis['performance_issues']
        })
    
    def log_memory_results(self, analysis):
        """Log memory profiling results"""
        
        frappe.log_error(f"Memory Profile: {analysis['function']}", {
            'total_memory_mb': analysis['total_memory_mb'],
            'peak_memory_mb': analysis['peak_memory_mb'],
            'memory_hotspots': analysis['memory_hotspots'][:3],
            'memory_issues': analysis['memory_issues']
        })
```

### 42.5 Client-Side Debugging

**Browser Developer Tools and Frontend Debugging**

```javascript
// Client-side debugging tools
class ClientSideDebugger {
    constructor() {
        this.debugMode = this.getDebugMode();
        this.performanceMonitor = new PerformanceMonitor();
        this.errorHandler = new ErrorHandler();
        this.networkMonitor = new NetworkMonitor();
        this.setupDebugging();
    }
    
    getDebugMode() {
        // Check for debug mode in various ways
        return (
            window.location.search.includes('debug=1') ||
            localStorage.getItem('erpnext_debug') === 'true' ||
            frappe.boot.debug === 1
        );
    }
    
    setupDebugging() {
        if (this.debugMode) {
            this.enableConsoleLogging();
            this.enablePerformanceMonitoring();
            this.enableNetworkMonitoring();
            this.addDebugUI();
        }
    }
    
    enableConsoleLogging() {
        // Enhanced console logging
        const originalLog = console.log;
        const originalError = console.error;
        const originalWarn = console.warn;
        
        console.log = (...args) => {
            originalLog.apply(console, ['[ERPNext Debug]', ...args]);
            this.sendToServer('LOG', args);
        };
        
        console.error = (...args) => {
            originalError.apply(console, ['[ERPNext Error]', ...args]);
            this.sendToServer('ERROR', args);
        };
        
        console.warn = (...args) => {
            originalWarn.apply(console, ['[ERPNext Warning]', ...args]);
            this.sendToServer('WARNING', args);
        };
    }
    
    enablePerformanceMonitoring() {
        // Monitor page performance
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            
            const metrics = {
                'page_load_time': perfData.loadEventEnd - perfData.navigationStart,
                'dom_ready_time': perfData.domContentLoadedEventEnd - perfData.navigationStart,
                'first_paint': perfData.paintTiming.firstPaint - perfData.navigationStart,
                'resources_loaded': perfData.loadEventEnd - perfData.domContentLoadedEventEnd
            };
            
            console.log('Performance Metrics:', metrics);
            this.sendToServer('PERFORMANCE', metrics);
        });
    }
    
    enableNetworkMonitoring() {
        // Monitor network requests
        const originalFetch = window.fetch;
        const originalXHR = window.XMLHttpRequest;
        
        window.fetch = async (...args) => {
            const start = performance.now();
            
            try {
                const response = await originalFetch.apply(window, args);
                const end = performance.now();
                
                this.logNetworkCall('fetch', args[0], response, end - start);
                return response;
            } catch (error) {
                this.logNetworkError('fetch', args[0], error, end - start);
                throw error;
            }
        };
        
        // Override XMLHttpRequest for older requests
        const XHR = function() {
            const xhr = new originalXHR();
            const originalOpen = xhr.open;
            const originalSend = xhr.send;
            
            xhr.open = (method, url, ...args) => {
                xhr._method = method;
                xhr._url = url;
                xhr._start = performance.now();
                return originalOpen.apply(xhr, [method, url, ...args]);
            };
            
            xhr.send = (data) => {
                const start = xhr._start;
                
                xhr.addEventListener('loadend', () => {
                    const end = performance.now();
                    this.logNetworkCall('xhr', xhr._url, xhr, end - start);
                });
                
                return originalSend.apply(xhr, [data]);
            };
            
            return xhr;
        };
        
        window.XMLHttpRequest = XHR;
    }
    
    logNetworkCall(type, url, response, duration) {
        const logData = {
            'type': type,
            'url': url,
            'method': response._method || 'GET',
            'status': response.status || response.statusText,
            'duration_ms': duration,
            'response_size': this.getResponseSize(response),
            'timestamp': new Date().toISOString()
        };
        
        console.log('Network Call:', logData);
        this.sendToServer('NETWORK', logData);
    }
    
    logNetworkError(type, url, error, duration) {
        const logData = {
            'type': type,
            'url': url,
            'error': error.message || error,
            'duration_ms': duration,
            'timestamp': new Date().toISOString()
        };
        
        console.error('Network Error:', logData);
        this.sendToServer('NETWORK_ERROR', logData);
    }
    
    getResponseSize(response) {
        // Calculate response size
        if (response.headers && response.headers.get('content-length')) {
            return parseInt(response.headers.get('content-length'));
        } else if (response.responseText) {
            return new Blob([response.responseText]).size;
        }
        return 0;
    }
    
    sendToServer(level, data) {
        // Send debugging data to server
        fetch('/api/method/log_client_debug', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': frappe.csrf_token
            },
            body: JSON.stringify({
                'level': level,
                'data': data,
                'url': window.location.href,
                'user_agent': navigator.userAgent,
                'timestamp': new Date().toISOString()
            })
        }).catch(error => {
            console.error('Failed to send debug data:', error);
        });
    }
    
    addDebugUI() {
        // Add debug UI to page
        const debugPanel = document.createElement('div');
        debugPanel.id = 'erpnext-debug-panel';
        debugPanel.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            width: 300px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 15px;
            border-radius: 5px;
            z-index: 10000;
            font-family: monospace;
            font-size: 12px;
            max-height: 400px;
            overflow-y: auto;
        `;
        
        debugPanel.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 10px;">
                ERPNext Debug Panel
            </div>
            <div>
                <button onclick="togglePerformanceMonitor()">Performance</button>
                <button onclick="toggleNetworkMonitor()">Network</button>
                <button onclick="showConsoleLogs()">Console</button>
                <button onclick="runDiagnostics()">Diagnostics</button>
            </div>
            <div id="debug-content" style="margin-top: 10px;"></div>
        `;
        
        document.body.appendChild(debugPanel);
        
        // Make functions globally available
        window.togglePerformanceMonitor = () => this.performanceMonitor.toggle();
        window.toggleNetworkMonitor = () => this.networkMonitor.toggle();
        window.showConsoleLogs = () => this.showConsoleLogs();
        window.runDiagnostics = () => this.runDiagnostics();
    }
    
    runDiagnostics() {
        const diagnostics = {
            'erpnext_version': frappe.boot.version,
            'app_version': frappe.boot.app_version,
            'user_language': frappe.boot.language,
            'timezone': frappe.boot.timezone,
            'permissions': frappe.boot.user.permissions,
            'active_modules': Object.keys(frappe.boot.modules),
            'browser_info': {
                'name': navigator.appName,
                'version': navigator.appVersion,
                'platform': navigator.platform,
                'user_agent': navigator.userAgent
            },
            'screen_info': {
                'width': screen.width,
                'height': screen.height,
                'color_depth': screen.colorDepth
            },
            'connection_info': navigator.connection || {
                'effective_type': 'unknown',
                'downlink': 'unknown',
                'rtt': 'unknown'
            }
        };
        
        document.getElementById('debug-content').innerHTML = `
            <h4>System Diagnostics</h4>
            <pre>${JSON.stringify(diagnostics, null, 2)}</pre>
        `;
        
        console.log('Diagnostics:', diagnostics);
        this.sendToServer('DIAGNOSTICS', diagnostics);
    }
}

// Initialize debugger
const debugger = new ClientSideDebugger();

// Usage examples for debugging
function debugFrappeCall(method, args) {
    console.log(`Calling Frappe method: ${method}`, args);
    
    const start = performance.now();
    
    return frappe.call({
        method: method,
        args: args,
        callback: function(r) {
            const end = performance.now();
            console.log(`Frappe method ${method} completed in ${end - start}ms`, r);
        }
    });
}

function debugFormSubmission(form) {
    form.addEventListener('submit', (e) => {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        console.log('Form submission:', data);
        
        // Validate before submission
        const validation = validateFormData(data);
        if (!validation.valid) {
            console.error('Form validation failed:', validation.errors);
            e.preventDefault();
        }
    });
}

function validateFormData(data) {
    // Example validation logic
    const errors = [];
    
    if (!data.customer) {
        errors.push('Customer is required');
    }
    
    if (!data.transaction_date) {
        errors.push('Transaction date is required');
    }
    
    return {
        valid: errors.length === 0,
        errors: errors
    };
}
```

### 42.6 Production Debugging Strategies

**Debugging in Production Environments**

```python
# Production debugging strategies
class ProductionDebugger:
    """Safe debugging strategies for production environments"""
    
    def __init__(self):
        self.safe_debug_mode = self._get_safe_debug_mode()
        self.production_logs = ProductionLogManager()
        self.error_tracker = ErrorTracker()
        self.performance_monitor = ProductionPerformanceMonitor()
    
    def _get_safe_debug_mode(self):
        """Get safe debug mode configuration"""
        
        return {
            'enabled': frappe.get_system_settings('enable_safe_debug'),
            'allowed_users': frappe.get_system_settings('debug_allowed_users', '').split(','),
            'log_level': frappe.get_system_settings('debug_log_level', 'ERROR'),
            'features': {
                'request_tracing': frappe.get_system_settings('debug_request_tracing', False),
                'sql_logging': frappe.get_system_settings('debug_sql_logging', False),
                'performance_profiling': frappe.get_system_settings('debug_performance_profiling', False),
                'error_details': frappe.get_system_settings('debug_error_details', True)
            }
        }
    
    def safe_debug_log(self, level, message, context=None):
        """Safe logging for production"""
        
        # Check if debugging is enabled for this user
        if not self._is_debug_allowed():
            return
        
        # Check log level
        min_level = self.safe_debug_mode['log_level']
        if level < min_level:
            return
        
        # Sanitize context for production
        safe_context = self._sanitize_context(context)
        
        # Log with production-safe details
        log_entry = {
            'timestamp': frappe.utils.now(),
            'level': level,
            'message': message,
            'context': safe_context,
            'user': frappe.session.user,
            'request_id': getattr(frappe.local, 'request_id', None)
        }
        
        # Send to production logging system
        self.production_logs.log(log_entry)
    
    def _is_debug_allowed(self):
        """Check if debug is allowed for current user"""
        
        if not self.safe_debug_mode['enabled']:
            return False
        
        current_user = frappe.session.user
        allowed_users = self.safe_debug_mode['allowed_users']
        
        return current_user in allowed_users
    
    def _sanitize_context(self, context):
        """Sanitize context for production logging"""
        
        if not context:
            return {}
        
        safe_context = {}
        sensitive_keys = ['password', 'secret', 'token', 'key', 'credit_card', 'ssn']
        
        for key, value in context.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                safe_context[key] = '[REDACTED]'
            elif isinstance(value, str) and len(value) > 200:
                safe_context[key] = value[:200] + '...'
            else:
                safe_context[key] = value
        
        return safe_context
    
    def trace_request(self, request_data):
        """Trace request for debugging"""
        
        if not self.safe_debug_mode['features']['request_tracing']:
            return
        
        trace_data = {
            'request_id': getattr(frappe.local, 'request_id', None),
            'timestamp': frappe.utils.now(),
            'method': request_data.method,
            'path': request_data.path,
            'headers': dict(request_data.headers),
            'user': frappe.session.user,
            'ip_address': frappe.local.request_ip,
            'user_agent': request_data.headers.get('User-Agent'),
            'form_data': self._sanitize_form_data(request_data.form_dict),
            'query_params': request_data.args
        }
        
        self.production_logs.trace_request(trace_data)
    
    def monitor_slow_operations(self, operation, threshold_seconds=30):
        """Monitor slow operations in production"""
        
        if not self.safe_debug_mode['features']['performance_profiling']:
            return
        
        # Context manager for monitoring
        class SlowOperationMonitor:
            def __init__(self, op_name, threshold):
                self.op_name = op_name
                self.threshold = threshold
                self.start_time = None
            
            def __enter__(self):
                self.start_time = frappe.utils.now()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.start_time:
                    duration = (frappe.utils.now() - self.start_time).total_seconds()
                    
                    if duration > self.threshold:
                        frappe.log_error(f"Slow operation detected: {self.op_name}", {
                            'duration_seconds': duration,
                            'threshold_seconds': self.threshold,
                            'user': frappe.session.user,
                            'request_id': getattr(frappe.local, 'request_id', None)
                        })
        
        return SlowOperationMonitor(operation, threshold_seconds)
    
    def create_error_report(self, error, context=None):
        """Create detailed error report for production"""
        
        error_report = {
            'error_id': frappe.generate_hash(length=8),
            'timestamp': frappe.utils.now(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': frappe.get_traceback(),
            'context': context or {},
            'user': frappe.session.user,
            'request_id': getattr(frappe.local, 'request_id', None),
            'system_info': self._get_system_info(),
            'browser_info': self._get_browser_info()
        }
        
        # Store error report
        self.error_tracker.report_error(error_report)
        
        # Send notification for critical errors
        if self._is_critical_error(error):
            self._send_error_notification(error_report)
    
    def _is_critical_error(self, error):
        """Determine if error is critical"""
        
        critical_errors = [
            'DatabaseError',
            'ConnectionError',
            'AuthenticationError',
            'PermissionError'
        ]
        
        return any(isinstance(error, critical_error) for critical_error in critical_errors)
    
    def _get_system_info(self):
        """Get system information for error reporting"""
        
        return {
            'erpnext_version': frappe.__version__,
            'python_version': sys.version,
            'database_version': frappe.db.get_database_version(),
            'server_info': frappe.local.request.environ if hasattr(frappe.local, 'request') else {},
            'memory_usage': self._get_memory_usage(),
            'disk_usage': self._get_disk_usage()
        }
    
    def _get_browser_info(self):
        """Get browser information from request"""
        
        request = getattr(frappe.local, 'request', None)
        if not request:
            return {}
        
        return {
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': frappe.local.request_ip,
            'referrer': request.headers.get('Referer'),
            'language': request.headers.get('Accept-Language')
        }
```

## 🎯 Chapter Summary

### Key Takeaways

1. **Use Multiple Debugging Layers**
   - Application logging for business logic issues
   - Framework debugging for Frappe internals
   - Database debugging for query performance
   - Performance profiling for optimization

2. **Implement Structured Logging**
   - Use structured log formats with context
   - Include performance metrics in logs
   - Sanitize sensitive information
   - Use appropriate log levels

3. **Profile Systematically**
   - Profile both CPU and memory usage
   - Monitor database query performance
   - Track API response times
   - Identify bottlenecks proactively

4. **Debug Safely in Production**
   - Use safe debugging modes with user restrictions
   - Implement request tracing for specific users
   - Monitor slow operations automatically
   - Create detailed error reports

### Implementation Checklist

- [ ] **Logging Framework**: Implement structured logging system
- [ ] **Performance Monitoring**: Set up profiling and monitoring tools
- [ ] **Database Debugging**: Configure slow query analysis
- [ ] **Client-Side Tools**: Implement browser debugging tools
- [ ] **Production Debugging**: Set up safe production debugging
- [ ] **Error Tracking**: Create comprehensive error reporting
- [ ] **Alerting**: Implement alerting for critical issues
- [ ] **Documentation**: Document debugging procedures

**Remember**: Good debugging practices reduce troubleshooting time and improve system reliability. Invest in debugging tools and training for better problem-solving capabilities.

---

**Next Chapter**: Advanced Topics and Future Trends
