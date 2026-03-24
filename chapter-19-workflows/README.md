# Chapter 19: Workflows — Document Approval Processes

## Learning Objectives

By the end of this chapter you will understand:
- What workflows are and when to use them
- States, transitions, and docstatus — how they relate
- How to create workflows via UI and programmatically
- Role-based transition control and conditional logic
- JavaScript and Python APIs for workflow operations

---

## 19.1 What Is a Workflow?

A workflow defines the **approval lifecycle** of a document — the states it can be in, who can move it between states, and under what conditions.

Without a workflow, a submittable document has three states: Draft → Submitted → Cancelled.

With a workflow, you can add intermediate states like "Pending Approval", "Under Review", "Rejected" — each mapped to one of the three underlying docstatus values (0, 1, 2).

**Key rule**: Workflows only work on **submittable DocTypes** (DocTypes with `is_submittable = 1`).

---

## 19.2 Core Concepts

### docstatus vs workflow_state

These are two separate fields that work together:

| Field | Type | Values | Purpose |
|-------|------|--------|---------|
| `docstatus` | System field | 0, 1, 2 | Controls submission state |
| `workflow_state` | Custom Link field | State names | Tracks business process stage |

```
docstatus 0 = Draft     → can be edited
docstatus 1 = Submitted → read-only (except allow_on_submit fields)
docstatus 2 = Cancelled → read-only, can be amended
```

A workflow state like "Pending Approval" is just a name — it maps to `docstatus = 0` under the hood. "Approved" maps to `docstatus = 1`. You can have many named states all mapping to the same docstatus.

### The flow constraint

```
0 → 1 → 2   (valid)
0 → 2        (invalid — cannot cancel without submitting)
1 → 0        (invalid — cannot revert a submitted document)
```

Frappe enforces this. You cannot create a transition that violates this order.

---

## 19.3 Workflow Components

### States

Each state has:

| Property | Description |
|----------|-------------|
| State Name | Display name (e.g. "Pending Approval") |
| Doc Status | 0, 1, or 2 |
| Only Allow Edit For | Role that can edit the document in this state |
| Update Field | Optional field to update when entering this state |
| Update Value | Value to set in Update Field |
| Send Email On State | Send notification email on entering this state |

### Transitions

Each transition has:

| Property | Description |
|----------|-------------|
| State | The current state (from) |
| Action | Button label shown to the user |
| Next State | The target state (to) |
| Allowed | Role that can execute this transition |
| Allow Self Approval | Can the document creator approve their own doc? |
| Condition | Python expression — must evaluate to `True` |

---

## 19.4 Creating a Workflow via UI

1. Go to **Setup → Workflow → New**
2. Set **Document Type** (must be submittable)
3. Set **Workflow State Field** (default: `workflow_state`)
4. Add **States** — at minimum: one Draft state (docstatus=0) and one Approved state (docstatus=1)
5. Add **Transitions** connecting the states
6. Save

### Example: Purchase Order approval

```
States:
  Draft          → docstatus 0, editable by "Purchase User"
  Pending Review → docstatus 0, editable by "Purchase Manager"
  Approved       → docstatus 1
  Rejected       → docstatus 0, editable by "Purchase User"

Transitions:
  Draft          → [Submit for Review]  → Pending Review   (allowed: Purchase User)
  Pending Review → [Approve]            → Approved         (allowed: Purchase Manager)
  Pending Review → [Reject]             → Rejected         (allowed: Purchase Manager)
  Rejected       → [Resubmit]           → Pending Review   (allowed: Purchase User)
```

---

## 19.5 Conditional Transitions

The `condition` field accepts a Python expression evaluated in a sandboxed context. The `doc` variable is available as a dictionary.

```python
# Only allow approval if grand total is under 10,000
doc.grand_total < 10000

# Only allow if a required field is filled
doc.get("custom_approval_note")

# Date-based condition
frappe.utils.getdate(doc.required_by) >= frappe.utils.getdate(frappe.utils.nowdate())
```

Available in the sandbox: `doc`, `frappe.db.get_value()`, `frappe.db.get_list()`, `frappe.session`, and `frappe.utils` date helpers.

---

## 19.6 Python API

```python
from frappe.model.workflow import (
    apply_workflow,
    get_transitions,
    get_workflow,
    get_workflow_name,
)

# Get the workflow for a DocType
workflow = get_workflow("Purchase Order")

# Get available transitions for a document
doc = frappe.get_doc("Purchase Order", "PO-00001")
transitions = get_transitions(doc)
# Returns list of transition dicts: action, next_state, allowed, condition

# Apply a workflow action
updated_doc = apply_workflow(doc, "Approve")
# Handles: state update, docstatus change, comment, email notifications

# Query documents by workflow state
pending = frappe.get_all(
    "Purchase Order",
    filters={"workflow_state": "Pending Review", "docstatus": 0},
    fields=["name", "supplier", "grand_total"],
)
```

### Auto-approve based on amount

```python
# hooks.py
doc_events = {
    "Purchase Order": {
        "on_update": "my_app.workflow_logic.auto_approve_small_orders"
    }
}

# workflow_logic.py
def auto_approve_small_orders(doc, method):
    if doc.grand_total >= 1000:
        return
    workflow_name = get_workflow_name(doc.doctype)
    if not workflow_name:
        return
    transitions = get_transitions(doc)
    approve = next((t for t in transitions if t["action"] == "Approve"), None)
    if approve:
        apply_workflow(doc, "Approve")
```

### Bulk workflow operations

```python
from frappe.model.workflow import bulk_workflow_approval

# For > 20 documents this automatically queues a background job
bulk_workflow_approval(
    docnames=["PO-00001", "PO-00002", "PO-00003"],
    doctype="Purchase Order",
    action="Approve",
)
```

---

## 19.7 JavaScript API

```javascript
// Check if DocType has a workflow
const hasWorkflow = frappe.model.has_workflow(frm.doctype);

// Get current workflow state
const state = frappe.workflow.get_state(frm.doc);

// Get available transitions
frappe.workflow.get_transitions(frm.doc).then((transitions) => {
    transitions.forEach((t) => {
        console.log(t.action, "→", t.next_state, "(allowed:", t.allowed, ")");
    });
});

// Apply a workflow action programmatically
frappe.xcall("frappe.model.workflow.apply_workflow", {
    doc: frm.doc,
    action: "Approve",
}).then((updatedDoc) => {
    frappe.model.sync(updatedDoc);
    frm.refresh();
    frappe.show_alert({ message: __("Approved"), indicator: "green" });
});
```

### Form script hooks for workflow events

```javascript
frappe.ui.form.on("Purchase Order", {
    // Fires before a workflow action button is clicked
    before_workflow_action: function(frm) {
        if (frm.doc.grand_total > 50000 && !frm.doc.custom_cfo_sign_off) {
            frappe.throw(__("CFO sign-off required for orders above 50,000"));
        }
    },

    // Fires after the workflow action completes
    after_workflow_action: function(frm) {
        frappe.show_alert({ message: __("Workflow action completed"), indicator: "blue" });
    },
});
```

---

## 19.8 Common Workflow Patterns

### Simple approval

```
Draft → [Submit] → Pending → [Approve] → Approved
                           → [Reject]  → Rejected
```

### Multi-level approval

```
Draft → [Submit] → L1 Review → [Approve L1] → L2 Review → [Approve L2] → Approved
                             → [Reject]     → Rejected
                                            → [Reject]   → Rejected
```

### Review cycle (document can go back)

```
Draft → [Submit for Review] → Under Review → [Request Changes] → Draft
                                           → [Approve]         → Approved
```

---

## 19.9 Best Practices

1. **Plan on paper first** — draw the state diagram before touching the UI
2. **Use meaningful state names** — "Pending Finance Review" beats "State 2"
3. **Keep conditions simple** — complex logic belongs in a Python function, not inline
4. **Test with each role** — log in as each role and verify the correct buttons appear
5. **Use Update Field** — maintain a user-friendly `status` field alongside `workflow_state`
6. **Don't bypass `apply_workflow()`** — setting `workflow_state` directly skips validation, comments, and notifications

---

## Summary

Workflows add a business process layer on top of Frappe's document submission system. The key mental model:

- `docstatus` is the system-level state (0/1/2)
- `workflow_state` is the business-level state (any name you choose)
- States map names to docstatus values
- Transitions define who can move between states and under what conditions
- `apply_workflow(doc, action)` is the single correct way to trigger transitions programmatically

---

**Next Chapter**: Translations and Internationalization — making your app speak every language.
