# Chapter 7: Client-Side Mastery with JavaScript

## 🎯 Learning Objectives

By the end of this chapter, you will master:

- The `cur_frm` object: properties and methods deep dive
- Form events: `setup`, `refresh`, `onload`, `before_save`, `after_save`
- Field events: `onload`, `change`, `onclick` handlers
- `frappe.call`: calling whitelisted methods from client
- Dynamic UI manipulation: adding/removing rows, hiding/showing sections
- Custom buttons and action menus
- Working with dialogs and modals programmatically

## 📚 Chapter Topics

### 7.1 The cur_frm Object Deep Dive

#### Understanding cur_frm

The `cur_frm` (current form) object is the central JavaScript object that represents the current document form in Frappe. It provides access to all form elements, fields, and methods.

#### Core Properties

```javascript
// Basic properties
cur_frm.doctype                    // Current DocType name
cur_frm.docname                    // Current document name
cur_frm.doc                        // Current document data
cur_frm.docstatus                  // Document status (0=Draft, 1=Submitted, 2=Cancelled)
cur_frm.is_new()                   // Check if document is new
cur_frm.is_dirty()                 // Check if document has unsaved changes

// Document access
cur_frm.get_doc()                  // Get complete document object
cur_frm.get_field(fieldname)       // Get field object
cur_frm.get_value(fieldname)       // Get field value
cur_frm.set_value(fieldname, value) // Set field value

// Form state
cur_frm.read_only                  // Check if form is read-only
cur_frm.perm                        // User permissions for current form
cur_frm.fields_dict                // Dictionary of all field objects
```

#### Essential Methods

```javascript
// Navigation and refresh
cur_frm.refresh()                  // Refresh the form
cur_frm.reload_doc()               // Reload document from server
cur_frm.cscript                    // Execute server script

// Field manipulation
cur_frm.add_custom_button(label, action, btn_class)  // Add custom button
cur_frm.remove_custom_button(label)                 // Remove custom button
cur_frm.set_intro(label)                            // Set intro message
cur_frm.clear_intro()                               // Clear intro message

// Validation and saving
cur_frm.validate()                 // Validate form
cur_frm.save()                     // Save document
cur_frm.save_or_update()           // Save or update document
cur_frm.saves()                    // Check if document can be saved

// Child table operations
cur_frm.get_field(fieldname).grid  // Get child table grid
cur_frm.get_grid(fieldname)        // Get child table grid (alias)
cur_frm.add_child(child_doc)       // Add child record
cur_frm.reload_doc()               // Reload document
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
