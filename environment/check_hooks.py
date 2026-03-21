"""Find all ERPNext doc_events hooks that fire on Asset"""
import frappe

def run():
    # Get all doc_events registered across all apps
    all_hooks = frappe.get_hooks('doc_events')
    
    print("=== doc_events for 'Asset' ===")
    for event, handlers in all_hooks.get('Asset', {}).items():
        print(f"  {event}: {handlers}")
    
    print("\n=== doc_events for '*' (all doctypes) ===")
    for event, handlers in all_hooks.get('*', {}).items():
        print(f"  {event}: {handlers}")
    
    # Also check what fields ERPNext's accounting_period hook needs
    print("\n=== Fields needed by accounting_period hook ===")
    print("  asset_type, available_for_use_date, company")
