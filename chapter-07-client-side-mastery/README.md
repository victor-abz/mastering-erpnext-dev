# Chapter 7: Client-Side Mastery with JavaScript

## 🎯 Learning Objectives

By the end of this chapter, you will master:

- **How** the Frappe client-side architecture manages form rendering and state
- **Why** different event patterns have specific performance characteristics
- **When** to use asynchronous operations for optimal user experience
- **How** JavaScript performance optimization impacts form responsiveness
- **Advanced patterns** for complex UI interactions and state management
- **Performance optimization** techniques for high-volume client-side operations

## 📚 Chapter Topics

### 7.1 Understanding the Frappe Client-Side Architecture

**The Client-Side Rendering Engine**

The Frappe client-side architecture is a sophisticated system that manages form rendering, state synchronization, and user interactions. Understanding its internal workings is crucial for building high-performance, responsive applications.

#### How Forms Are Rendered and Managed

```javascript
// Simplified version of Frappe's form rendering system
class FormRenderer {
    constructor(doctype, docname) {
        this.doctype = doctype;
        this.docname = docname;
        this.form_container = null;
        this.field_cache = new Map();
        this.event_handlers = new Map();
        this.state_manager = new FormStateManager();
        this.performance_monitor = new PerformanceMonitor();
        
        // Initialize form
        this.initialize_form();
    }
    
    initialize_form() {
        // Load form metadata
        this.load_form_meta();
        
        // Create form structure
        this.create_form_structure();
        
        // Render fields
        this.render_fields();
        
        // Bind events
        this.bind_events();
        
        // Initialize state
        this.initialize_state();
    }
    
    load_form_meta() {
        // Load DocType metadata
        frappe.model.with_doctype(this.doctype, () => {
            this.meta = frappe.get_meta(this.doctype);
            this.fields = this.meta.fields;
            this.layouts = this.meta.layouts;
        });
    }
    
    create_form_structure() {
        // Create form container
        this.form_container = $('<div class="form-layout"></div>');
        
        // Create sections based on layout
        this.meta.sections.forEach(section => {
            const section_el = this.create_section(section);
            this.form_container.append(section_el);
        });
        
        // Append to page
        $('.form-page').append(this.form_container);
    }
    
    render_fields() {
        const start_time = performance.now();
        
        // Render each field
        this.fields.forEach(field => {
            const field_element = this.render_field(field);
            this.field_cache.set(field.fieldname, field_element);
        });
        
        // Track rendering performance
        const render_time = performance.now() - start_time;
        this.performance_monitor.track_metric('field_rendering', render_time);
    }
    
    render_field(field) {
        const field_wrapper = $(`
            <div class="frappe-control" 
                 data-fieldname="${field.fieldname}" 
                 data-fieldtype="${field.fieldtype}">
                <div class="control-label">${field.label}</div>
                <div class="control-input"></div>
            </div>
        `);
        
        // Create field-specific input
        const input_element = this.create_field_input(field);
        field_wrapper.find('.control-input').append(input_element);
        
        // Add field-specific classes
        field_wrapper.addClass(`input-${field.fieldtype}`);
        
        // Add validation classes
        if (field.reqd) {
            field_wrapper.addClass('required');
        }
        
        return field_wrapper;
    }
    
    create_field_input(field) {
        const field_type = field.fieldtype;
        
        switch (field_type) {
            case 'Data':
                return $('<input type="text" class="form-control">')
                    .attr('maxlength', field.length || 255);
            
            case 'Text':
                return $('<textarea class="form-control">')
                    .attr('rows', field.rows || 4);
            
            case 'Link':
                return this.create_link_field(field);
            
            case 'Select':
                return this.create_select_field(field);
            
            case 'Date':
                return $('<input type="date" class="form-control">');
            
            case 'Datetime':
                return $('<input type="datetime-local" class="form-control">');
            
            case 'Check':
                return $('<input type="checkbox" class="form-control">');
            
            case 'Currency':
                return $('<input type="number" class="form-control" step="0.01">');
            
            case 'Table':
                return this.create_child_table(field);
            
            default:
                return $('<input type="text" class="form-control">');
        }
    }
    
    create_link_field(field) {
        const wrapper = $('<div class="link-field-wrapper"></div>');
        const input = $('<input type="text" class="form-control">');
        const button = $('<button type="button" class="btn btn-default">...</button>');
        
        // Add autocomplete functionality
        input.autocomplete({
            source: (request, response) => {
                frappe.call({
                    method: 'frappe.desk.search.search_link',
                    args: {
                        doctype: field.options,
                        txt: request.term
                    },
                    callback: (r) => {
                        response(r.results);
                    }
                });
            },
            select: (event, ui) => {
                input.val(ui.item.value);
                this.trigger_field_change(field.fieldname, ui.item.value);
            }
        });
        
        // Add button click handler
        button.on('click', () => {
            this.show_link_selector(field, input);
        });
        
        wrapper.append(input).append(button);
        return wrapper;
    }
    
    create_select_field(field) {
        const select = $('<select class="form-control">');
        
        // Add options
        if (field.options) {
            const options = field.options.split('\n');
            options.forEach(option => {
                const option_el = $('<option>')
                    .val(option)
                    .text(option);
                select.append(option_el);
            });
        }
        
        // Add change handler
        select.on('change', () => {
            this.trigger_field_change(field.fieldname, select.val());
        });
        
        return select;
    }
    
    create_child_table(field) {
        const table_wrapper = $('<div class="child-table-wrapper"></div>');
        const table = $('<table class="table table-bordered child-table"></table>');
        const thead = $('<thead></thead>');
        const tbody = $('<tbody></tbody>');
        
        // Create table headers
        const child_meta = frappe.get_meta(field.options);
        const header_row = $('<tr></tr>');
        
        child_meta.fields.forEach(child_field => {
            if (child_field.in_list_view) {
                const th = $('<th>')
                    .text(child_field.label)
                    .attr('data-fieldname', child_field.fieldname);
                header_row.append(th);
            }
        });
        
        thead.append(header_row);
        table.append(thead).append(tbody);
        table_wrapper.append(table);
        
        // Add add row button
        const add_button = $('<button type="button" class="btn btn-sm btn-primary">Add Row</button>');
        add_button.on('click', () => {
            this.add_child_row(field, tbody);
        });
        
        table_wrapper.append(add_button);
        return table_wrapper;
    }
    
    bind_events() {
        // Bind form-level events
        this.bind_form_events();
        
        // Bind field events
        this.bind_field_events();
        
        // Bind keyboard shortcuts
        this.bind_keyboard_shortcuts();
    }
    
    bind_form_events() {
        // Form save event
        $(document).on('click', '.btn-save', () => {
            this.save_form();
        });
        
        // Form refresh event
        $(document).on('form-refresh', () => {
            this.refresh_form();
        });
        
        // Form validation event
        $(document).on('form-validate', () => {
            this.validate_form();
        });
    }
    
    bind_field_events() {
        // Field change events
        this.field_cache.forEach((field_element, fieldname) => {
            const input = field_element.find('input, select, textarea');
            
            input.on('change', (e) => {
                const value = $(e.target).val();
                this.trigger_field_change(fieldname, value);
            });
            
            input.on('focus', (e) => {
                this.trigger_field_focus(fieldname);
            });
            
            input.on('blur', (e) => {
                this.trigger_field_blur(fieldname);
            });
        });
    }
    
    bind_keyboard_shortcuts() {
        // Ctrl+S to save
        $(document).on('keydown', (e) => {
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.save_form();
            }
        });
        
        // Ctrl+N for new document
        $(document).on('keydown', (e) => {
            if (e.ctrlKey && e.key === 'n') {
                e.preventDefault();
                this.new_document();
            }
        });
    }
    
    trigger_field_change(fieldname, value) {
        const start_time = performance.now();
        
        // Update form state
        this.state_manager.set_field_value(fieldname, value);
        
        // Execute field change handlers
        if (this.event_handlers.has(fieldname)) {
            const handlers = this.event_handlers.get(fieldname);
            handlers.forEach(handler => {
                handler(value);
            });
        }
        
        // Track performance
        const change_time = performance.now() - start_time;
        this.performance_monitor.track_metric('field_change', change_time);
    }
    
    save_form() {
        const start_time = performance.now();
        
        // Validate form
        if (!this.validate_form()) {
            return;
        }
        
        // Get form data
        const form_data = this.get_form_data();
        
        // Save to server
        frappe.call({
            method: 'frappe.client.save',
            args: {
                doc: form_data
            },
            callback: (r) => {
                if (r.docs) {
                    this.on_save_success(r.docs[0]);
                }
            },
            error: (err) => {
                this.on_save_error(err);
            }
        });
        
        // Track performance
        const save_time = performance.now() - start_time;
        this.performance_monitor.track_metric('form_save', save_time);
    }
    
    validate_form() {
        let is_valid = true;
        
        // Validate required fields
        this.field_cache.forEach((field_element, fieldname) => {
            const field = this.fields.find(f => f.fieldname === fieldname);
            const input = field_element.find('input, select, textarea');
            const value = input.val();
            
            if (field.reqd && !value) {
                field_element.addClass('has-error');
                is_valid = false;
            } else {
                field_element.removeClass('has-error');
            }
        });
        
        return is_valid;
    }
    
    get_form_data() {
        const form_data = {
            doctype: this.doctype,
            name: this.docname
        };
        
        // Get field values
        this.field_cache.forEach((field_element, fieldname) => {
            const input = field_element.find('input, select, textarea');
            const value = input.val();
            
            if (value) {
                form_data[fieldname] = value;
            }
        });
        
        return form_data;
    }
}
```

#### Form State Management System

```javascript
// Advanced form state management
class FormStateManager {
    constructor() {
        this.state = new Map();
        this.history = [];
        this.max_history_size = 50;
        this.subscribers = new Map();
        this.validation_rules = new Map();
        this.dependencies = new Map();
    }
    
    set_field_value(fieldname, value) {
        const old_value = this.state.get(fieldname);
        
        // Only update if value changed
        if (old_value !== value) {
            // Save to history
            this.save_to_history(fieldname, old_value, value);
            
            // Update state
            this.state.set(fieldname, value);
            
            // Trigger validation
            this.validate_field(fieldname, value);
            
            // Update dependencies
            this.update_dependencies(fieldname, value);
            
            // Notify subscribers
            this.notify_subscribers(fieldname, value, old_value);
        }
    }
    
    get_field_value(fieldname) {
        return this.state.get(fieldname);
    }
    
    get_all_values() {
        const values = {};
        this.state.forEach((value, fieldname) => {
            values[fieldname] = value;
        });
        return values;
    }
    
    save_to_history(fieldname, old_value, new_value) {
        this.history.push({
            fieldname,
            old_value,
            new_value,
            timestamp: Date.now()
        });
        
        // Limit history size
        if (this.history.length > this.max_history_size) {
            this.history.shift();
        }
    }
    
    subscribe(fieldname, callback) {
        if (!this.subscribers.has(fieldname)) {
            this.subscribers.set(fieldname, []);
        }
        
        this.subscribers.get(fieldname).push(callback);
    }
    
    unsubscribe(fieldname, callback) {
        if (this.subscribers.has(fieldname)) {
            const callbacks = this.subscribers.get(fieldname);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }
    
    notify_subscribers(fieldname, new_value, old_value) {
        if (this.subscribers.has(fieldname)) {
            const callbacks = this.subscribers.get(fieldname);
            callbacks.forEach(callback => {
                callback(new_value, old_value);
            });
        }
    }
    
    add_validation_rule(fieldname, rule) {
        if (!this.validation_rules.has(fieldname)) {
            this.validation_rules.set(fieldname, []);
        }
        
        this.validation_rules.get(fieldname).push(rule);
    }
    
    validate_field(fieldname, value) {
        if (this.validation_rules.has(fieldname)) {
            const rules = this.validation_rules.get(fieldname);
            
            for (const rule of rules) {
                const result = rule(value);
                if (!result.valid) {
                    this.show_validation_error(fieldname, result.message);
                    return false;
                }
            }
        }
        
        this.clear_validation_error(fieldname);
        return true;
    }
    
    add_dependency(fieldname, depends_on, condition) {
        if (!this.dependencies.has(fieldname)) {
            this.dependencies.set(fieldname, []);
        }
        
        this.dependencies.get(fieldname).push({
            depends_on,
            condition
        });
    }
    
    update_dependencies(fieldname, value) {
        this.state.forEach((field_value, dep_fieldname) => {
            if (this.dependencies.has(dep_fieldname)) {
                const dependencies = this.dependencies.get(dep_fieldname);
                
                dependencies.forEach(dep => {
                    if (dep.depends_on === fieldname) {
                        const should_show = dep.condition(value);
                        this.toggle_field_visibility(dep_fieldname, should_show);
                    }
                });
            }
        });
    }
    
    toggle_field_visibility(fieldname, visible) {
        const field_element = $(`.frappe-control[data-fieldname="${fieldname}"]`);
        
        if (visible) {
            field_element.show();
        } else {
            field_element.hide();
        }
    }
    
    show_validation_error(fieldname, message) {
        const field_element = $(`.frappe-control[data-fieldname="${fieldname}"]`);
        field_element.addClass('has-error');
        
        // Remove existing error message
        field_element.find('.validation-error').remove();
        
        // Add new error message
        const error_element = $('<div class="validation-error text-danger">')
            .text(message);
        field_element.append(error_element);
    }
    
    clear_validation_error(fieldname) {
        const field_element = $(`.frappe-control[data-fieldname="${fieldname}"]`);
        field_element.removeClass('has-error');
        field_element.find('.validation-error').remove();
    }
    
    undo() {
        if (this.history.length > 0) {
            const last_change = this.history.pop();
            this.state.set(last_change.fieldname, last_change.old_value);
            this.notify_subscribers(last_change.fieldname, last_change.old_value, last_change.new_value);
        }
    }
    
    redo() {
        // Implementation for redo functionality
        // This would require maintaining a separate redo stack
    }
    
    reset() {
        this.state.clear();
        this.history = [];
        this.subscribers.clear();
    }
}
```

#### Performance Monitoring System

```javascript
// Client-side performance monitoring
class PerformanceMonitor {
    constructor() {
        this.metrics = new Map();
        this.thresholds = {
            field_rendering: 100,  // 100ms
            field_change: 50,      // 50ms
            form_save: 1000,       // 1s
            server_call: 2000      // 2s
        };
        this.slow_operations = [];
        this.performance_report = null;
    }
    
    track_metric(operation, duration) {
        if (!this.metrics.has(operation)) {
            this.metrics.set(operation, {
                count: 0,
                total_time: 0,
                min_time: Infinity,
                max_time: 0,
                avg_time: 0
            });
        }
        
        const metric = this.metrics.get(operation);
        metric.count++;
        metric.total_time += duration;
        metric.min_time = Math.min(metric.min_time, duration);
        metric.max_time = Math.max(metric.max_time, duration);
        metric.avg_time = metric.total_time / metric.count;
        
        // Check if operation is slow
        if (duration > this.thresholds[operation]) {
            this.slow_operations.push({
                operation,
                duration,
                timestamp: Date.now()
            });
            
            // Log slow operation
            console.warn(`Slow ${operation}: ${duration}ms (threshold: ${this.thresholds[operation]}ms)`);
        }
    }
    
    track_server_call(method, start_time, end_time, success) {
        const duration = end_time - start_time;
        
        this.track_metric('server_call', duration);
        
        // Track specific method
        const method_name = method.split('.').pop();
        if (!this.metrics.has(method_name)) {
            this.metrics.set(method_name, {
                count: 0,
                total_time: 0,
                min_time: Infinity,
                max_time: 0,
                avg_time: 0
            });
        }
        
        const method_metric = this.metrics.get(method_name);
        method_metric.count++;
        method_metric.total_time += duration;
        method_metric.min_time = Math.min(method_metric.min_time, duration);
        method_metric.max_time = Math.max(method_metric.max_time, duration);
        method_metric.avg_time = method_metric.total_time / method_metric.count;
        
        if (!success) {
            console.error(`Failed server call: ${method} (${duration}ms)`);
        }
    }
    
    get_performance_report() {
        const report = {
            timestamp: Date.now(),
            metrics: {},
            slow_operations: this.slow_operations,
            recommendations: []
        };
        
        // Convert metrics to plain object
        this.metrics.forEach((metric, operation) => {
            report.metrics[operation] = {
                count: metric.count,
                total_time: Math.round(metric.total_time),
                min_time: Math.round(metric.min_time),
                max_time: Math.round(metric.max_time),
                avg_time: Math.round(metric.avg_time)
            };
        });
        
        // Generate recommendations
        report.recommendations = this.generate_recommendations();
        
        return report;
    }
    
    generate_recommendations() {
        const recommendations = [];
        
        // Check for slow field rendering
        if (this.metrics.has('field_rendering')) {
            const rendering_metric = this.metrics.get('field_rendering');
            if (rendering_metric.avg_time > 50) {
                recommendations.push({
                    type: 'performance',
                    message: 'Field rendering is slow. Consider optimizing field layout or reducing field count.',
                    severity: 'medium'
                });
            }
        }
        
        // Check for slow form saves
        if (this.metrics.has('form_save')) {
            const save_metric = this.metrics.get('form_save');
            if (save_metric.avg_time > 500) {
                recommendations.push({
                    type: 'performance',
                    message: 'Form save is slow. Consider optimizing server-side validation or reducing data size.',
                    severity: 'high'
                });
            }
        }
        
        // Check for slow server calls
        if (this.metrics.has('server_call')) {
            const server_metric = this.metrics.get('server_call');
            if (server_metric.avg_time > 1000) {
                recommendations.push({
                    type: 'performance',
                    message: 'Server calls are slow. Consider optimizing API methods or adding caching.',
                    severity: 'high'
                });
            }
        }
        
        return recommendations;
    }
    
    reset_metrics() {
        this.metrics.clear();
        this.slow_operations = [];
    }
    
    export_metrics() {
        return JSON.stringify(this.get_performance_report(), null, 2);
    }
}
```

### 7.2 Form Events

#### Event Lifecycle

```javascript
// Form Setup - Called when form is initialized
cur_frm.cscript.setup = function(doc, cdt, cdn) {
    console.log("Form setup called");
    
    // Set default values
    if (doc.docstatus === 0 && !doc.transaction_date) {
        doc.transaction_date = frappe.datetime.nowdate();
    }
    
    // Add custom CSS
    cur_frm.add_custom_button("Custom Action", function() {
        frappe.msgprint("Custom action triggered!");
    }, "btn-primary");
};

// Form Load - Called when document is loaded
cur_frm.cscript.onload = function(doc, cdt, cdn) {
    console.log("Form loaded");
    
    // Perform operations after document loads
    if (doc.customer) {
        // Load customer details
        frappe.call({
            method: "my_app.api.get_customer_details",
            args: { customer: doc.customer },
            callback: function(r) {
                if (r.message) {
                    // Update form with customer details
                    cur_frm.set_value("credit_limit", r.message.credit_limit);
                }
            }
        });
    }
};

// Form Refresh - Called when form is refreshed
cur_frm.cscript.refresh = function(doc, cdt, cdn) {
    console.log("Form refreshed");
    
    // Show/hide buttons based on document status
    if (doc.docstatus === 1) {
        // Document is submitted
        cur_frm.remove_custom_button("Submit");
        cur_frm.add_custom_button("Cancel", function() {
            cur_frm.cscript.cancel_document(doc);
        });
    }
    
    // Update field visibility
    cur_frm.cscript.update_field_visibility(doc);
};

// Before Save - Called before document is saved
cur_frm.cscript.before_save = function(doc, cdt, cdn) {
    console.log("Before save");
    
    // Validate business logic
    if (doc.grand_total > 100000 && !doc.approval_required) {
        frappe.msgprint({
            title: "High Value Order",
            message: "Orders above $100,000 require approval",
            indicator: "red"
        });
        frappe.validated = false;
    }
    
    // Calculate totals
    cur_frm.cscript.calculate_totals(doc);
};

// After Save - Called after document is saved
cur_frm.cscript.after_save = function(doc, cdt, cdn) {
    console.log("After save");
    
    // Send notifications
    if (doc.docstatus === 1) {
        frappe.call({
            method: "my_app.api.send_order_confirmation",
            args: { order: doc.name },
            callback: function(r) {
                if (r.message) {
                    frappe.show_alert("Order confirmation sent");
                }
            }
        });
    }
};
```

#### Advanced Event Handling

```javascript
// Document submission
cur_frm.cscript.on_submit = function(doc, cdt, cdn) {
    console.log("Document submitted");
    
    // Create follow-up tasks
    frappe.call({
        method: "my_app.api.create_delivery_task",
        args: { sales_order: doc.name },
        callback: function(r) {
            if (r.message) {
                frappe.show_alert({
                    message: "Delivery task created",
                    indicator: "green"
                });
            }
        }
    });
};

// Document cancellation
cur_frm.cscript.on_cancel = function(doc, cdt, cdn) {
    console.log("Document cancelled");
    
    // Cancel related documents
    if (doc.delivery_notes && doc.delivery_notes.length > 0) {
        frappe.call({
            method: "my_app.api.cancel_related_deliveries",
            args: { sales_order: doc.name },
            callback: function(r) {
                if (r.message) {
                    frappe.show_alert("Related deliveries cancelled");
                }
            }
        });
    }
};

// Custom validation
cur_frm.cscript.validate = function(doc, cdt, cdn) {
    console.log("Validating document");
    
    // Custom validation logic
    if (doc.items && doc.items.length > 0) {
        var total_qty = 0;
        for (var i = 0; i < doc.items.length; i++) {
            total_qty += doc.items[i].qty || 0;
        }
        
        if (total_qty > 1000) {
            frappe.msgprint("Total quantity cannot exceed 1000 units");
            frappe.validated = false;
            return;
        }
    }
    
    frappe.validated = true;
};
```

### 7.3 Field Events

#### Field Change Events

```javascript
// Customer field change
cur_frm.cscript.customer = function(doc, cdt, cdn) {
    var customer = doc.customer;
    
    if (customer) {
        // Load customer details
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Customer",
                name: customer
            },
            callback: function(r) {
                if (r.docs && r.docs[0]) {
                    var customer_doc = r.docs[0];
                    
                    // Update customer group
                    cur_frm.set_value("customer_group", customer_doc.customer_group);
                    
                    // Update territory
                    cur_frm.set_value("territory", customer_doc.territory);
                    
                    // Update credit limit
                    cur_frm.set_value("credit_limit", customer_doc.credit_limit);
                    
                    // Refresh form
                    cur_frm.refresh_fields();
                }
            }
        });
        
        // Load customer's previous orders
        cur_frm.cscript.load_customer_orders(doc, customer);
    } else {
        // Clear dependent fields
        cur_frm.set_value("customer_group", "");
        cur_frm.set_value("territory", "");
        cur_frm.set_value("credit_limit", 0);
    }
};

// Item field change in child table
cur_frm.cscript.item_code = function(doc, cdt, cdn) {
    var d = locals[cdt][cdn];
    var item_code = d.item_code;
    
    if (item_code) {
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Item",
                name: item_code
            },
            callback: function(r) {
                if (r.docs && r.docs[0]) {
                    var item_doc = r.docs[0];
                    
                    // Update item details
                    frappe.model.set_value(cdt, cdn, "item_name", item_doc.item_name);
                    frappe.model.set_value(cdt, cdn, "description", item_doc.description);
                    frappe.model.set_value(cdt, cdn, "uom", item_doc.stock_uom);
                    frappe.model.set_value(cdt, cdn, "rate", item_doc.formatted_price);
                    
                    // Update stock status
                    cur_frm.cscript.update_stock_status(doc, cdt, cdn, item_code);
                }
            }
        });
    }
};

// Quantity field change
cur_frm.cscript.qty = function(doc, cdt, cdn) {
    var d = locals[cdt][cdn];
    var qty = d.qty || 0;
    var rate = d.rate || 0;
    
    // Calculate amount
    var amount = qty * rate;
    frappe.model.set_value(cdt, cdn, "amount", amount);
    
    // Update totals
    cur_frm.cscript.calculate_totals(doc);
    
    // Check stock availability
    if (d.item_code && qty > 0) {
        cur_frm.cscript.check_stock_availability(doc, d.item_code, qty);
    }
};
```

#### Field Focus and Blur Events

```javascript
// Field focus event
cur_frm.cscript.customer_on_focus = function(doc, cdt, cdn) {
    console.log("Customer field focused");
    
    // Show customer help
    cur_frm.set_intro("Select a customer from the dropdown or type to search");
};

// Field blur event
cur_frm.cscript_customer_on_blur = function(doc, cdt, cdn) {
    console.log("Customer field blurred");
    
    // Clear intro message
    cur_frm.clear_intro();
    
    // Validate customer selection
    if (doc.customer && !frappe.db.exists("Customer", doc.customer)) {
        frappe.msgprint("Invalid customer selected");
        cur_frm.set_value("customer", "");
    }
};
```

### 7.4 Server Communication with frappe.call

#### Basic frappe.call Usage

```javascript
// Simple server call
function get_customer_balance(customer) {
    frappe.call({
        method: "my_app.api.get_customer_balance",
        args: { customer: customer },
        callback: function(r) {
            if (r.message) {
                cur_frm.set_value("customer_balance", r.message.balance);
                cur_frm.set_value("credit_used", r.message.credit_used);
            }
        },
        error: function(err) {
            frappe.msgprint("Error fetching customer balance");
        }
    });
}

// Call with whitelisted method
function calculate_shipping_cost(items, address) {
    frappe.call({
        method: "my_app.api.calculate_shipping",
        args: {
            items: items,
            shipping_address: address
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                cur_frm.set_value("shipping_cost", r.message.cost);
                cur_frm.cscript.calculate_totals(cur_frm.doc);
            }
        },
        freeze: true,
        freeze_message: "Calculating shipping cost..."
    });
}
```

#### Advanced frappe.call Patterns

```javascript
// Multiple calls in sequence
function load_complete_order_data(order_name) {
    // First, get order details
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Sales Order",
            name: order_name
        },
        callback: function(r) {
            if (r.docs && r.docs[0]) {
                var order = r.docs[0];
                
                // Then get customer details
                frappe.call({
                    method: "frappe.client.get",
                    args: {
                        doctype: "Customer",
                        name: order.customer
                    },
                    callback: function(customer_r) {
                        if (customer_r.docs && customer_r.docs[0]) {
                            var customer = customer_r.docs[0];
                            
                            // Update form with complete data
                            cur_frm.set_value("customer_name", customer.customer_name);
                            cur_frm.set_value("customer_group", customer.customer_group);
                            
                            // Load items
                            cur_frm.cscript.load_items_from_order(order);
                        }
                    }
                });
            }
        }
    });
}

// Parallel calls with Promise
function load_order_summary(order_name) {
    var promises = [];
    
    // Get order details
    promises.push(
        frappe.call({
            method: "frappe.client.get",
            args: { doctype: "Sales Order", name: order_name }
        })
    );
    
    // Get customer details
    promises.push(
        frappe.call({
            method: "frappe.client.get",
            args: { doctype: "Customer", name: cur_frm.doc.customer }
        })
    );
    
    // Get item details
    promises.push(
        frappe.call({
            method: "my_app.api.get_item_details",
            args: { items: cur_frm.doc.items }
        })
    );
    
    // Wait for all calls to complete
    Promise.all(promises).then(function(results) {
        var order = results[0].message;
        var customer = results[1].message;
        var items = results[2].message;
        
        // Process results
        cur_frm.cscript.update_order_summary(order, customer, items);
    });
}
```

### 7.5 Dynamic UI Manipulation

#### Field Visibility and Dependencies

```javascript
// Show/hide fields based on conditions
function update_field_visibility(doc) {
    var is_submitted = doc.docstatus === 1;
    var has_items = doc.items && doc.items.length > 0;
    
    // Hide fields for submitted documents
    if (is_submitted) {
        cur_frm.toggle_display("customer", false);
        cur_frm.toggle_display("transaction_date", false);
        cur_frm.toggle_reqd("customer", false);
    } else {
        cur_frm.toggle_display("customer", true);
        cur_frm.toggle_display("transaction_date", true);
        cur_frm.toggle_reqd("customer", true);
    }
    
    // Show totals only if items exist
    cur_frm.toggle_display("total_amount", has_items);
    cur_frm.toggle_display("grand_total", has_items);
    
    // Show approval fields for high-value orders
    if (doc.grand_total > 50000) {
        cur_frm.toggle_display("approval_required", true);
        cur_frm.toggle_reqd("approval_notes", true);
    } else {
        cur_frm.toggle_display("approval_required", false);
        cur_frm.toggle_reqd("approval_notes", false);
    }
}

// Set field dependencies
function set_field_dependencies() {
    // Make delivery date required if shipping is needed
    cur_frm.add_dependency("requires_shipping", "delivery_date", function() {
        return cur_frm.doc.requires_shipping === 1;
    });
    
    // Show warranty fields only for specific items
    cur_frm.add_dependency("item_group", "warranty_period", function() {
        return cur_frm.doc.item_group === "Electronics";
    });
}
```

#### Child Table Manipulation

```javascript
// Add child row with default values
function add_item_row(item_code) {
    var child = cur_frm.add_child("items");
    child.item_code = item_code;
    child.qty = 1;
    child.uom = "Nos";
    
    // Refresh child table
    cur_frm.refresh_field("items");
    
    // Focus on quantity field
    cur_frm.get_field("items").grid.grid_rows[cur_frm.get_field("items").grid.grid_rows.length - 1].toggle_editable("qty");
}

// Remove child row with validation
function remove_item_row(row_index) {
    var items = cur_frm.doc.items;
    var item_to_remove = items[row_index];
    
    // Check if item can be removed
    if (item_to_remove.delivered_qty > 0) {
        frappe.msgprint("Cannot remove item that has been delivered");
        return;
    }
    
    // Remove row
    cur_frm.get_field("items").grid.grid_rows[row_index].remove();
    
    // Recalculate totals
    cur_frm.cscript.calculate_totals(cur_frm.doc);
}

// Update child table based on conditions
function update_item_prices(doc) {
    var items = doc.items || [];
    var price_list = doc.price_list;
    
    if (!price_list) {
        frappe.msgprint("Please select a price list");
        return;
    }
    
    // Get prices for all items
    var item_codes = items.map(function(item) { return item.item_code; });
    
    frappe.call({
        method: "my_app.api.get_item_prices",
        args: {
            items: item_codes,
            price_list: price_list
        },
        callback: function(r) {
            if (r.message && r.message.prices) {
                var prices = r.message.prices;
                
                // Update each item's price
                items.forEach(function(item, index) {
                    if (prices[item.item_code]) {
                        frappe.model.set_value("Sales Order Item", item.name, "rate", prices[item.item_code]);
                    }
                });
                
                // Refresh and calculate totals
                cur_frm.refresh_field("items");
                cur_frm.cscript.calculate_totals(doc);
            }
        },
        freeze: true,
        freeze_message: "Updating prices..."
    });
}
```

#### Section and Tab Manipulation

```javascript
// Show/hide sections
function toggle_sections(doc) {
    var has_attachments = doc.attachments && doc.attachments.length > 0;
    var is_international = doc.customer_country && doc.customer_country !== frappe.sys_defaults.country;
    
    // Show attachments section if attachments exist
    cur_frm.toggle_display("attachments_section", has_attachments);
    
    // Show international shipping section
    cur_frm.toggle_display("international_shipping", is_international);
    
    // Collapse/expand sections
    if (doc.docstatus === 1) {
        cur_frm.collapse_section("basic_info");
        cur_frm.expand_section("delivery_details");
    }
}

// Add custom tab
function add_custom_tab() {
    if (!cur_frm.tabs_dict["custom_info"]) {
        cur_frm.add_custom_tab("Custom Info", function() {
            // Custom tab content
            return `
                <div class="custom-tab-content">
                    <h4>Custom Information</h4>
                    <p>This is custom content for the document.</p>
                    <div id="custom-data"></div>
                </div>
            `;
        });
        
        // Load custom data when tab is shown
        cur_frm.tabs_dict["custom_info"].on_show = function() {
            load_custom_data();
        };
    }
}

function load_custom_data() {
    frappe.call({
        method: "my_app.api.get_custom_info",
        args: { docname: cur_frm.docname },
        callback: function(r) {
            if (r.message) {
                var custom_data = document.getElementById("custom-data");
                if (custom_data) {
                    custom_data.innerHTML = JSON.stringify(r.message, null, 2);
                }
            }
        }
    });
}
```

### 7.6 Custom Buttons and Actions

#### Adding Custom Buttons

```javascript
// Add custom button in setup
cur_frm.cscript.setup = function(doc, cdt, cdn) {
    // Add primary action button
    cur_frm.add_custom_button("Generate Invoice", function() {
        cur_frm.cscript.generate_invoice(doc);
    }, "btn-primary");
    
    // Add secondary action button
    cur_frm.add_custom_button("Send Email", function() {
        cur_frm.cscript.send_email(doc);
    });
    
    // Add custom menu
    cur_frm.add_custom_button("Actions", function() {
        // Show dropdown menu
        cur_frm.cscript.show_actions_menu(doc);
    }, "btn-default");
    
    // Add button conditionally
    if (doc.docstatus === 1) {
        cur_frm.add_custom_button("Create Delivery", function() {
            cur_frm.cscript.create_delivery(doc);
        }, "btn-success");
    }
};

// Button actions
cur_frm.cscript.generate_invoice = function(doc) {
    frappe.call({
        method: "my_app.api.create_sales_invoice",
        args: { sales_order: doc.name },
        callback: function(r) {
            if (r.message && r.message.invoice) {
                frappe.show_alert({
                    message: "Invoice created: " + r.message.invoice,
                    indicator: "green"
                });
                
                // Open new invoice
                frappe.set_route("Form", "Sales Invoice", r.message.invoice);
            }
        },
        freeze: true,
        freeze_message: "Generating invoice..."
    });
};

cur_frm.cscript.send_email = function(doc) {
    frappe.call({
        method: "my_app.api.send_order_email",
        args: { order: doc.name },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.show_alert("Email sent successfully");
            }
        },
        freeze: true,
        freeze_message: "Sending email..."
    });
};

cur_frm.cscript.show_actions_menu = function(doc) {
    var actions = [
        {
            label: "Print Order",
            action: function() {
                window.open("/printview?doctype=Sales%20Order&name=" + doc.name);
            }
        },
        {
            label: "Duplicate Order",
            action: function() {
                cur_frm.cscript.duplicate_order(doc);
            }
        },
        {
            label: "Export to Excel",
            action: function() {
                cur_frm.cscript.export_to_excel(doc);
            }
        }
    ];
    
    // Show menu
    frappe.prompt([
        {
            fieldname: "action",
            fieldtype: "Select",
            options: actions.map(function(a) { return a.label; }).join("\n"),
            label: "Select Action"
        }
    ], function(data) {
        var selected_action = actions.find(function(a) { return a.label === data.action; });
        if (selected_action) {
            selected_action.action();
        }
    }, "Select Action", "Execute");
};
```

#### Dynamic Button Management

```javascript
// Update buttons based on document state
function update_buttons(doc) {
    // Remove existing custom buttons
    cur_frm.remove_custom_button("Generate Invoice");
    cur_frm.remove_custom_button("Send Email");
    cur_frm.remove_custom_button("Create Delivery");
    
    // Add buttons based on conditions
    if (doc.docstatus === 0) {
        // Draft document
        cur_frm.add_custom_button("Generate Invoice", function() {
            cur_frm.cscript.generate_invoice(doc);
        }, "btn-primary");
        
        cur_frm.add_custom_button("Send Email", function() {
            cur_frm.cscript.send_email(doc);
        });
        
    } else if (doc.docstatus === 1) {
        // Submitted document
        if (!doc.invoice_created) {
            cur_frm.add_custom_button("Generate Invoice", function() {
                cur_frm.cscript.generate_invoice(doc);
            }, "btn-primary");
        }
        
        if (!doc.delivery_created && doc.items.some(item => item.delivered_qty < item.qty)) {
            cur_frm.add_custom_button("Create Delivery", function() {
                cur_frm.cscript.create_delivery(doc);
            }, "btn-success");
        }
        
        cur_frm.add_custom_button("Send Email", function() {
            cur_frm.cscript.send_email(doc);
        });
    }
}

// Add contextual buttons
function add_contextual_buttons(doc) {
    // Add button based on customer type
    if (doc.customer_group === "Government") {
        cur_frm.add_custom_button("Generate PO", function() {
            cur_frm.cscript.generate_purchase_order(doc);
        }, "btn-warning");
    }
    
    // Add button based on order value
    if (doc.grand_total > 100000) {
        cur_frm.add_custom_button("Request Approval", function() {
            cur_frm.cscript.request_approval(doc);
        }, "btn-danger");
    }
}
```

### 7.7 Dialogs and Modals

#### Custom Dialogs

```javascript
// Show custom dialog
function show_item_selection_dialog() {
    var dialog = new frappe.ui.Dialog({
        title: "Select Items",
        fields: [
            {
                fieldname: "item_group",
                fieldtype: "Link",
                options: "Item Group",
                label: "Item Group",
                change: function() {
                    // Filter items based on group
                    dialog.set_df_property("items", "get_query", function() {
                        return {
                            filters: {
                                item_group: dialog.get_value("item_group")
                            }
                        };
                    });
                }
            },
            {
                fieldname: "items",
                fieldtype: "Table",
                label: "Items",
                options: "Sales Order Item",
                get_query: function() {
                    return {
                        filters: {
                            disabled: 0
                        }
                    };
                }
            }
        ],
        primary_action: function(values) {
            // Add selected items to order
            values.items.forEach(function(item) {
                if (item.item_code) {
                    cur_frm.cscript.add_item_row(item.item_code);
                }
            });
            
            dialog.hide();
            cur_frm.refresh_fields();
        },
        primary_action_label: "Add Items"
    });
    
    dialog.show();
}

// Show confirmation dialog
function confirm_order_cancellation() {
    frappe.confirm(
        "Are you sure you want to cancel this order? This action cannot be undone.",
        function() {
            // User confirmed
            cur_frm.cscript.cancel_order();
        },
        function() {
            // User cancelled
            frappe.msgprint("Order cancellation cancelled");
        }
    );
}

// Show prompt dialog
function prompt_for_approval_notes() {
    frappe.prompt([
        {
            fieldname: "approval_notes",
            fieldtype: "Text",
            label: "Approval Notes",
            reqd: 1
        },
        {
            fieldname: "approver",
            fieldtype: "Link",
            options: "User",
            label: "Approver",
            reqd: 1,
            default: frappe.session.user
        }
    ], function(values) {
        // Submit for approval
        cur_frm.cscript.submit_for_approval(values);
    }, "Submit for Approval", "Submit");
}
```

#### Advanced Modal Windows

```javascript
// Show custom modal with HTML content
function show_order_summary_modal() {
    var modal = new frappe.ui.Dialog({
        title: "Order Summary",
        size: "large",
        fields: [
            {
                fieldtype: "HTML",
                fieldname: "summary_html"
            }
        ],
        primary_action: function() {
            modal.hide();
        },
        primary_action_label: "Close"
    });
    
    // Generate summary HTML
    var summary_html = cur_frm.cscript.generate_order_summary_html(cur_frm.doc);
    modal.get_field("summary_html").$wrapper.html(summary_html);
    
    modal.show();
}

// Generate order summary HTML
cur_frm.cscript.generate_order_summary_html = function(doc) {
    var html = `
        <div class="order-summary">
            <div class="row">
                <div class="col-md-6">
                    <h4>Order Information</h4>
                    <p><strong>Order:</strong> ${doc.name}</p>
                    <p><strong>Date:</strong> ${doc.transaction_date}</p>
                    <p><strong>Customer:</strong> ${doc.customer_name}</p>
                    <p><strong>Status:</strong> ${doc.status}</p>
                </div>
                <div class="col-md-6">
                    <h4>Financial Summary</h4>
                    <p><strong>Total Amount:</strong> ${frappe.format(doc.total_amount, {fieldtype: "Currency"})}</p>
                    <p><strong>Tax:</strong> ${frappe.format(doc.total_taxes_and_charges, {fieldtype: "Currency"})}</p>
                    <p><strong>Grand Total:</strong> ${frappe.format(doc.grand_total, {fieldtype: "Currency"})}</p>
                </div>
            </div>
            <div class="row">
                <div class="col-md-12">
                    <h4>Items</h4>
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Item Code</th>
                                <th>Item Name</th>
                                <th>Quantity</th>
                                <th>Rate</th>
                                <th>Amount</th>
                            </tr>
                        </thead>
                        <tbody>
    `;
    
    // Add items to table
    (doc.items || []).forEach(function(item) {
        html += `
            <tr>
                <td>${item.item_code}</td>
                <td>${item.item_name}</td>
                <td>${item.qty}</td>
                <td>${frappe.format(item.rate, {fieldtype: "Currency"})}</td>
                <td>${frappe.format(item.amount, {fieldtype: "Currency"})}</td>
            </tr>
        `;
    });
    
    html += `
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
    
    return html;
};

// Show progress modal for long operations
function show_progress_modal(title, steps) {
    var progress_modal = new frappe.ui.Dialog({
        title: title,
        fields: [
            {
                fieldtype: "HTML",
                fieldname: "progress_html"
            }
        ],
        primary_action: function() {
            progress_modal.hide();
        },
        primary_action_label: "Close"
    });
    
    var progress_html = `
        <div class="progress-container">
            <div class="progress">
                <div class="progress-bar" role="progressbar" style="width: 0%">
                    0%
                </div>
            </div>
            <div class="steps">
    `;
    
    steps.forEach(function(step, index) {
        progress_html += `
            <div class="step" data-step="${index}">
                <div class="step-number">${index + 1}</div>
                <div class="step-label">${step.label}</div>
                <div class="step-status">pending</div>
            </div>
        `;
    });
    
    progress_html += `
            </div>
        </div>
    `;
    
    progress_modal.get_field("progress_html").$wrapper.html(progress_html);
    progress_modal.show();
    
    return progress_modal;
}
```

## 🛠️ Practical Exercises

### Exercise 7.1: Form Event Handling

Create a complete form with:
- Multiple field events
- Validation logic
- Dynamic field visibility
- Custom buttons

### Exercise 7.2: Server Communication

Implement client-server communication with:
- Multiple API calls
- Error handling
- Loading states
- Data caching

### Exercise 7.3: Dynamic UI Manipulation

Build dynamic forms with:
- Conditional field visibility
- Child table manipulation
- Custom dialogs
- Progress indicators

## 🚀 Best Practices

### JavaScript Code Organization

- **Use descriptive function names** for clarity
- **Organize code by functionality** in separate files
- **Handle errors gracefully** with user-friendly messages
- **Use proper event delegation** for dynamic content

### Performance Optimization

- **Minimize server calls** by caching data
- **Use debouncing** for frequently triggered events
- **Optimize DOM manipulation** with batch updates
- **Lazy load** non-critical features

### User Experience

- **Provide clear feedback** for all actions
- **Use loading indicators** for long operations
- **Implement proper validation** with helpful error messages
- **Ensure responsive design** for mobile devices

## 📖 Further Reading

- [Frappe Client API](https://frappeframework.com/docs/user/en/api/client)
- [JavaScript Best Practices](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [Frappe UI Framework](https://frappeframework.com/docs/user/en/ui)

## 🎯 Chapter Summary

Client-side mastery is crucial for creating responsive Frappe applications:

- **cur_frm object** provides complete form control
- **Form events** enable lifecycle management
- **Field events** handle user interactions
- **frappe.call** facilitates server communication
- **Dynamic UI manipulation** creates responsive interfaces
- **Custom buttons** enhance user workflows
- **Dialogs and modals** improve user experience

---

**Next Chapter**: Server script hooks and automation with schedulers.


---

## 📌 Addendum: API Correction — cur_frm.cscript is Deprecated

### The Old vs Modern Client Script API

The main chapter content uses `cur_frm.cscript.xxx = function(doc, cdt, cdn)` — this is the **legacy API** from Frappe v12 and earlier. It still works but is deprecated.

The **modern API** (v13+) is `frappe.ui.form.on(doctype, { event(frm) {} })`. Always use this in new code:

```javascript
// ❌ Old (deprecated) — cur_frm.cscript pattern
cur_frm.cscript.customer = function(doc, cdt, cdn) {
    // handle customer field change
};

cur_frm.cscript.refresh = function(doc, cdt, cdn) {
    // handle refresh
};

// ✅ Modern — frappe.ui.form.on pattern
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        // handle customer field change
    },
    refresh(frm) {
        // handle refresh
    }
});
```

Key differences:
- Modern API passes `frm` (the form object) — not `doc, cdt, cdn`
- Multiple handlers for the same event are supported (old API overwrites)
- Child table events use `frappe.ui.form.on('Child DocType', { field(frm, cdt, cdn) {} })`
- `frm.doc` gives you the document (equivalent to old `doc`)

---

## 📌 Addendum: frappe.ui.form.on vs frappe.provide, and Error Callbacks

### frappe.ui.form.on (Recommended — v14/v15)

`frappe.ui.form.on` is the standard event registration API in Frappe v14 and v15.  It is declarative, supports multiple handlers for the same event, and works correctly with Frappe's form lifecycle.

```javascript
frappe.ui.form.on('Sales Order', {
    // Fires when the form is refreshed (including on load)
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create Invoice'), () => {
                frappe.model.open_mapped_doc({
                    method: 'erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice',
                    frm: frm
                });
            });
        }
    },

    // Fires when the customer field value changes
    customer(frm) {
        if (!frm.doc.customer) return;
        frm.set_query('contact_person', () => ({
            filters: { link_doctype: 'Customer', link_name: frm.doc.customer }
        }));
    },

    // Child table field event — item_code changed in the items table
    'items.item_code'(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.item_code) {
            frappe.db.get_value('Item', row.item_code, 'standard_rate', (r) => {
                frappe.model.set_value(cdt, cdn, 'rate', r.standard_rate);
            });
        }
    }
});
```

### frappe.provide (Legacy — Avoid in New Code)

The older `frappe.provide` / `cur_frm.cscript` pattern pre-dates `frappe.ui.form.on`.  You will encounter it in older customisations and ERPNext source code, but it should not be used in new development.

```javascript
// ❌ Legacy — do not use in new code
frappe.provide('frappe.ui.form.cscript');
frappe.ui.form.cscript['Sales Order'] = class extends frappe.ui.form.cscript['Sales Order'] {
    customer(doc, cdt, cdn) {
        // ...
    }
};
```

### Always Add an error Callback for Critical API Calls

See `client_scripts/api_calls.js` — Examples 7–9 — for complete patterns including the `error` callback.  The `error` callback receives the raw XHR response object; `r.exc` contains the server traceback in developer mode.

```javascript
frappe.call({
    method: 'my_app.api.do_something',
    args: { name: frm.doc.name },
    callback(r) {
        if (r.message) frappe.show_alert('Done');
    },
    error(r) {
        frappe.msgprint({
            title: __('Error'),
            message: __('Operation failed. Please check error logs.'),
            indicator: 'red'
        });
    }
});
```


---

## Addendum: Source Article Insights

### Child Table Client Scripting (cdt, cdn, locals)

Child table scripting uses a three-argument pattern: `frm`, `cdt` (child doctype name), and `cdn` (child document name). The row data lives in `locals[cdt][cdn]`.

```javascript
// Register events on the child doctype, not the parent
frappe.ui.form.on("Sales Order Item", {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];  // Get the specific row

        if (row.item_code) {
            frappe.call({
                method: "frappe.client.get",
                args: { doctype: "Item", name: row.item_code },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
                        frappe.model.set_value(cdt, cdn, "rate", r.message.standard_rate || 0);
                        frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
                    }
                }
            });
        }
    },

    qty: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "amount", (row.qty || 0) * (row.rate || 0));
        calculate_grand_total(frm);
    },

    // Row add/remove events use fieldname + "_add" / "_remove"
    items_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // Set defaults for new rows
        frappe.model.set_value(cdt, cdn, "warehouse", frm.doc.warehouse);
    },

    items_remove: function(frm, cdt, cdn) {
        calculate_grand_total(frm);
    }
});

function calculate_grand_total(frm) {
    let total = (frm.doc.items || []).reduce((sum, row) => sum + (row.amount || 0), 0);
    frm.set_value("grand_total", total);
}
```

**Adding rows programmatically:**

```javascript
// Add a row with data
let new_row = frappe.model.add_child(frm.doc, "Sales Order Item", "items");
frappe.model.set_value(new_row.doctype, new_row.name, "item_code", "ITEM-001");
frappe.model.set_value(new_row.doctype, new_row.name, "qty", 5);
frm.refresh_field("items");

// Or using Object.assign after add_child
let row = frappe.model.add_child(frm.doc, "items", "items");
Object.assign(row, { item_code: "ITEM-001", qty: 5, rate: 100 });
frm.refresh_field("items");
```

**Filtering link fields in child tables:**

```javascript
frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        frm.set_query("item_code", "items", function() {
            return {
                filters: { is_sales_item: 1, disabled: 0 }
            };
        });
    }
});
```

**Toggle column visibility in child table:**

```javascript
frm.fields_dict.items.grid.toggle_display("warehouse", show_warehouse);
```

**Duplicate check in child table:**

```javascript
frappe.ui.form.on("Sales Order Item", {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicates = frm.doc.items.filter(r => r.item_code === row.item_code && r.name !== row.name);
        if (duplicates.length > 0) {
            frappe.msgprint("Duplicate item found.");
            frappe.model.set_value(cdt, cdn, "item_code", "");
        }
    }
});
```

---

### Custom Buttons: add_custom_button and make_custom_buttons

**`frm.add_custom_button`** adds a button to the form toolbar. Buttons can be grouped under a dropdown label.

```javascript
frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        // Simple button
        frm.add_custom_button("Send Reminder", function() {
            frappe.call({
                method: "my_app.api.send_reminder",
                args: { sales_order: frm.doc.name },
                callback: r => frappe.show_alert("Reminder sent")
            });
        });

        // Grouped button (appears in a dropdown)
        frm.add_custom_button("Create Invoice", function() {
            // action
        }, "Create");  // third arg = group name

        frm.add_custom_button("Create Delivery", function() {
            // action
        }, "Create");

        // Style a button (btn-primary, btn-success, btn-danger, etc.)
        frm.add_custom_button("Approve", function() {
            // action
        }).addClass("btn-success");
    }
});
```

**`frm.custom_make_buttons`** — declarative way to add "Make" buttons that create related documents. Frappe uses this pattern internally in ERPNext.

```javascript
frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        // Only show when submitted
        if (frm.doc.docstatus === 1) {
            frm.custom_make_buttons = {
                "Sales Invoice": "Make Invoice",
                "Delivery Note": "Make Delivery"
            };
        }
    }
});
```

**`frm.make_custom_buttons`** (alternative pattern) — maps doctype to button label, shown only when submitted:

```javascript
frappe.ui.form.on("Purchase Order", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.make_custom_buttons = {
                "Purchase Receipt": "Make Receipt",
                "Purchase Invoice": "Make Invoice"
            };
        }
    }
});
```

**Remove a custom button:**

```javascript
frm.remove_custom_button("Send Reminder");
// Or remove from a group:
frm.remove_custom_button("Create Invoice", "Create");
```

---

### Dialogs: frappe.ui.Dialog

`frappe.ui.Dialog` creates modal dialogs with form fields. It's the standard way to collect user input before performing an action.

```javascript
frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        frm.add_custom_button("Apply Discount", function() {
            let d = new frappe.ui.Dialog({
                title: "Apply Discount",
                fields: [
                    {
                        label: "Discount Type",
                        fieldname: "discount_type",
                        fieldtype: "Select",
                        options: ["Percentage\nFixed Amount"],
                        default: "Percentage",
                        reqd: 1
                    },
                    {
                        label: "Discount Value",
                        fieldname: "discount_value",
                        fieldtype: "Float",
                        reqd: 1
                    },
                    {
                        label: "Reason",
                        fieldname: "reason",
                        fieldtype: "Small Text"
                    }
                ],
                primary_action_label: "Apply",
                primary_action: function(values) {
                    // values contains the dialog field values
                    frappe.call({
                        method: "my_app.api.apply_discount",
                        args: {
                            sales_order: frm.doc.name,
                            discount_type: values.discount_type,
                            discount_value: values.discount_value,
                            reason: values.reason
                        },
                        callback: function(r) {
                            frm.reload_doc();
                            d.hide();
                        }
                    });
                }
            });
            d.show();
        });
    }
});
```

**Prompt (quick single-field dialog):**

```javascript
frappe.prompt(
    { label: "Reason for Cancellation", fieldname: "reason", fieldtype: "Small Text", reqd: 1 },
    function(values) {
        console.log(values.reason);
    },
    "Cancel Order",
    "Confirm"
);
```

**Confirm dialog:**

```javascript
frappe.confirm(
    "Are you sure you want to delete all items?",
    function() {
        // on yes
        frm.doc.items = [];
        frm.refresh_field("items");
    },
    function() {
        // on no (optional)
    }
);
```

**Dynamic field visibility in dialog:**

```javascript
let d = new frappe.ui.Dialog({
    title: "Configure",
    fields: [
        { fieldname: "mode", fieldtype: "Select", label: "Mode", options: "Auto\nManual" },
        { fieldname: "manual_value", fieldtype: "Float", label: "Value", depends_on: "eval:doc.mode=='Manual'" }
    ],
    primary_action: function(values) { d.hide(); }
});
d.show();
```

---

### Form Field $wrapper (jQuery Manipulation)

Every field in a Frappe form has a `$wrapper` property — a jQuery object wrapping the field's DOM element. This lets you inject HTML, apply CSS, or attach custom behavior.

```javascript
frappe.ui.form.on("Customer", {
    refresh: function(frm) {
        // Access the wrapper of a field
        let $wrapper = frm.fields_dict.customer_name.$wrapper;

        // Add a badge/indicator next to the field
        $wrapper.find(".control-label").append(
            '<span class="badge badge-info ml-2">VIP</span>'
        );

        // Inject custom HTML below the field input
        $wrapper.find(".control-input").after(
            '<div class="text-muted small mt-1">This name appears on all invoices</div>'
        );

        // Apply custom CSS
        $wrapper.find("input").css({
            "border-color": "#007bff",
            "font-weight": "bold"
        });
    }
});
```

**Inject a custom button inside a field wrapper:**

```javascript
frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        let $input_area = frm.fields_dict.customer.$wrapper.find(".control-input");
        $input_area.append(
            $('<button class="btn btn-xs btn-default ml-2">View History</button>')
                .on("click", function() {
                    frappe.set_route("List", "Sales Order", { customer: frm.doc.customer });
                })
        );
    }
});
```

**Highlight a section:**

```javascript
frm.fields_dict.payment_section.$wrapper.css("background-color", "#fff3cd");
```

**Access the raw input element:**

```javascript
let input_el = frm.fields_dict.email.$wrapper.find("input")[0];
input_el.setAttribute("placeholder", "Enter work email");
```

---

### ListView Customization (doctype_list.js)

Create a file at `your_app/public/js/{doctype_name}_list.js` (snake_case) to customize the list view for a DocType.

```javascript
// asset_list.js
frappe.listview_settings["Asset"] = {
    // Add extra fields to fetch (not shown as columns, but available in JS)
    add_fields: ["status", "asset_category", "location"],

    // Custom status indicator (colored dot in list)
    get_indicator: function(doc) {
        let color_map = {
            "Draft": "grey",
            "Submitted": "blue",
            "In Maintenance": "orange",
            "Scrapped": "red",
            "Fully Depreciated": "green"
        };
        return [doc.status, color_map[doc.status] || "grey", "status,=," + doc.status];
    },

    // Run code when list view loads
    onload: function(listview) {
        // Add a custom filter button
        listview.page.add_inner_button("My Assets", function() {
            listview.filter_area.add([[
                "Asset", "custodian", "=", frappe.session.user
            ]]);
        });
    },

    // Modify the query before it runs
    before_render: function() {
        // frappe.listview_settings["Asset"].filters = [["status", "!=", "Scrapped"]];
    },

    // Format a cell value
    formatters: {
        asset_value: function(value, df, doc) {
            return frappe.format(value, { fieldtype: "Currency" });
        }
    },

    // Right-click context menu items
    get_form_link: function(doc) {
        return `/app/asset/${doc.name}`;
    }
};
```

**Add a custom button to the list page:**

```javascript
frappe.listview_settings["Purchase Order"] = {
    onload: function(listview) {
        listview.page.add_action_item("Bulk Approve", function() {
            let selected = listview.get_checked_items();
            if (!selected.length) {
                frappe.msgprint("Select at least one record.");
                return;
            }
            frappe.call({
                method: "my_app.api.bulk_approve",
                args: { names: selected.map(d => d.name) },
                callback: () => listview.refresh()
            });
        });
    }
};
```

---

### Making Forms Read-Only

Several methods exist to restrict editing at different granularities.

**Disable the entire form (no editing, no save button):**

```javascript
frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        if (frm.doc.locked_by_finance) {
            frm.disable_form();
            frm.set_intro("This order is locked by Finance.", "orange");
        }
    }
});
```

**Disable save only (form is editable but can't be saved):**

```javascript
frm.disable_save();
```

**Make a specific field read-only dynamically:**

```javascript
frm.set_df_property("discount_percentage", "read_only", 1);
// Reverse it:
frm.set_df_property("discount_percentage", "read_only", 0);
```

**Make all fields read-only (but keep buttons):**

```javascript
frm.set_read_only();
```

**Conditionally lock fields based on status:**

```javascript
frappe.ui.form.on("Purchase Order", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            // Lock specific fields after submission
            ["supplier", "schedule_date", "currency"].forEach(f => {
                frm.set_df_property(f, "read_only", 1);
            });
        }
    }
});
```

**Read-only based on user role:**

```javascript
frappe.ui.form.on("Employee", {
    refresh: function(frm) {
        if (!frappe.user.has_role("HR Manager")) {
            frm.set_df_property("salary", "read_only", 1);
            frm.set_df_property("bank_account", "read_only", 1);
        }
    }
});
```
