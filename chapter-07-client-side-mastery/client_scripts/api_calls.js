/**
 * API Call Examples
 * Chapter 7: Client-Side Mastery
 * 
 * Demonstrates frappe.call() patterns
 */

// Example 1: Basic API Call
function get_customer_balance(customer) {
	frappe.call({
		method: 'erpnext.accounts.utils.get_balance_on',
		args: {
			party_type: 'Customer',
			party: customer,
			date: frappe.datetime.get_today()
		},
		callback: function(r) {
			if (r.message) {
				frappe.msgprint(__('Customer Balance: {0}', [format_currency(r.message)]));
			}
		}
	});
}

// Example 2: API Call with Error Handling
function create_sales_invoice_from_order(sales_order) {
	frappe.call({
		method: 'erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice',
		args: {
			source_name: sales_order
		},
		freeze: true,
		freeze_message: __('Creating Sales Invoice...'),
		callback: function(r) {
			if (r.message) {
				frappe.model.sync(r.message);
				frappe.set_route('Form', r.message.doctype, r.message.name);
			}
		},
		error: function(r) {
			frappe.msgprint({
				title: __('Error'),
				message: __('Failed to create Sales Invoice'),
				indicator: 'red'
			});
		}
	});
}

// Example 3: Async/Await Pattern
async function get_item_stock(item_code, warehouse) {
	try {
		const response = await frappe.call({
			method: 'erpnext.stock.utils.get_stock_balance',
			args: {
				item_code: item_code,
				warehouse: warehouse
			}
		});
		
		return response.message || 0;
	} catch (error) {
		console.error('Failed to get stock:', error);
		return 0;
	}
}

// Example 4: Multiple API Calls in Sequence
async function process_bulk_orders(orders) {
	let results = [];
	
	for (let order of orders) {
		try {
			const result = await frappe.call({
				method: 'custom_app.api.process_order',
				args: {
					order_id: order
				}
			});
			
			results.push({
				order: order,
				status: 'success',
				data: result.message
			});
		} catch (error) {
			results.push({
				order: order,
				status: 'failed',
				error: error.message
			});
		}
	}
	
	return results;
}

// Example 5: API Call with Progress Indicator
function import_bulk_data(file_url) {
	let progress_dialog = new frappe.ui.Dialog({
		title: __('Importing Data'),
		fields: [
			{
				fieldname: 'progress_html',
				fieldtype: 'HTML',
				options: '<div class="progress"><div class="progress-bar" style="width: 0%">0%</div></div>'
			}
		]
	});
	
	progress_dialog.show();
	
	frappe.call({
		method: 'custom_app.api.import_data',
		args: {
			file_url: file_url
		},
		callback: function(r) {
			if (r.message) {
				progress_dialog.hide();
				frappe.msgprint(__('Import completed: {0} records', [r.message.count]));
			}
		},
		// Update progress
		progress: function(progress) {
			let percent = Math.round(progress * 100);
			progress_dialog.fields_dict.progress_html.$wrapper.find('.progress-bar')
				.css('width', percent + '%')
				.text(percent + '%');
		}
	});
}

// Example 6: Batch API Calls
async function update_multiple_records(records) {
	const batch_size = 10;
	let batches = [];
	
	// Split into batches
	for (let i = 0; i < records.length; i += batch_size) {
		batches.push(records.slice(i, i + batch_size));
	}
	
	// Process batches
	for (let batch of batches) {
		await Promise.all(batch.map(record => 
			frappe.call({
				method: 'frappe.client.set_value',
				args: {
					doctype: record.doctype,
					name: record.name,
					fieldname: record.fieldname,
					value: record.value
				}
			})
		));
	}
	
	frappe.show_alert(__('All records updated'), 5);
}

// Example 7: frappe.ui.form.on Pattern (Recommended Modern Approach)
// Use frappe.ui.form.on instead of the older cur_frm.cscript pattern.
// frappe.ui.form.on is event-driven, supports multiple handlers, and is
// the standard in Frappe v14/v15.
frappe.ui.form.on('Sales Order', {
	customer: function(frm) {
		// Triggered when the customer field changes
		if (frm.doc.customer) {
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Customer',
					filters: { name: frm.doc.customer },
					fieldname: ['credit_limit', 'customer_group']
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('credit_limit', r.message.credit_limit);
					}
				},
				// Always add an error callback for production code
				error: function(r) {
					frappe.msgprint({
						title: __('Error'),
						message: __('Could not fetch customer details. Please try again.'),
						indicator: 'red'
					});
					console.error('Customer fetch error:', r);
				}
			});
		}
	},

	refresh: function(frm) {
		// Triggered on every form refresh
		frm.set_intro(__('Review items before submitting.'), 'blue');
	}
});

// Example 8: frappe.provide (Legacy Pattern — Avoid in New Code)
// The older frappe.provide / cur_frm.cscript approach is still functional
// but is considered legacy. Shown here for reference when maintaining
// older customizations.
//
// frappe.provide('frappe.ui.form.cscript');
// frappe.ui.form.cscript['Sales Order'] = frappe.ui.form.cscript['Sales Order'] || {};
// frappe.ui.form.cscript['Sales Order'].customer = function(doc, cdt, cdn) {
//     // Legacy handler — prefer frappe.ui.form.on above
// };

// Example 9: Explicit error callback pattern
// Always include an error callback when the result is critical to UX.
function submit_custom_action(doc_name) {
	frappe.call({
		method: 'custom_app.api.perform_action',
		args: { name: doc_name },
		freeze: true,
		freeze_message: __('Processing...'),
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({ message: __('Action completed'), indicator: 'green' });
				cur_frm.reload_doc();
			}
		},
		error: function(r) {
			// r.exc contains the server-side traceback (in developer mode)
			frappe.msgprint({
				title: __('Action Failed'),
				message: r.exc
					? __('Server error occurred. Check error logs.')
					: __('An unexpected error occurred.'),
				indicator: 'red'
			});
		}
	});
}
