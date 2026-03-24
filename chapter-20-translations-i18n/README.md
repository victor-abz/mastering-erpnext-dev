# Chapter 20: Translations and Internationalization (i18n)

## Learning Objectives

By the end of this chapter you will understand:
- How Frappe's translation system works at runtime
- How to add translations to your custom app
- Using `_()` in Python and `__()` in JavaScript
- Translation context — resolving ambiguous words
- Managing language files and when to rebuild

---

## 20.1 How Frappe Loads Translations

Frappe loads translations **dynamically at runtime** from CSV files in your app's `translations/` folder. No database migration or `bench migrate` is needed — just a browser refresh (or `bench clear-cache` if translations don't appear immediately).

The only time you need `bench build` is when you use `__()` in custom frontend JavaScript files that go through the asset bundler.

---

## 20.2 Setting Up Translations

### Step 1: Create the translations folder

```
apps/
  my_app/
    my_app/
      translations/       ← create this folder
        ar.csv            ← Arabic
        es.csv            ← Spanish
        fr.csv            ← French
```

The folder must be at the **root of your app's Python package** — the same level as `hooks.py`.

### Step 2: Create CSV files

Each file is named with the [ISO 639-1 language code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).

```csv
"source_string","translated_string","context"
"Welcome","مرحبا",""
"Save","حفظ",""
"Asset","أصل",""
```

Three columns:
1. `source_string` — the original string used in your code
2. `translated_string` — the translation
3. `context` — optional, used to disambiguate the same word with different meanings

### Step 3: Use translatable strings in code

**Python:**

```python
from frappe import _

def validate(doc, method):
    if not doc.asset_name:
        frappe.throw(_("Asset name is required"))

def get_status_label(status):
    labels = {
        "Active":   _("Active"),
        "Inactive": _("Inactive"),
        "Disposed": _("Disposed"),
    }
    return labels.get(status, status)
```

**JavaScript (client scripts):**

```javascript
frappe.ui.form.on("Asset", {
    refresh(frm) {
        frm.add_custom_button(__("Generate Report"), () => {
            frappe.msgprint(__("Report generated successfully"));
        });
    },
});
```

**Jinja templates (print formats, web pages):**

```html
<h1>{{ _("Asset Details") }}</h1>
<p>{{ _("Status") }}: {{ doc.status }}</p>
```

---

## 20.3 Translation Context

The same word can mean different things. Use context to disambiguate:

```csv
"charge","شحن","mobile phone charge"
"charge","رسوم","invoice line charge"
```

In code:

```python
# Without context — ambiguous
_("charge")

# With context — precise
_("charge", context="mobile phone charge")   # → شحن
_("charge", context="invoice line charge")   # → رسوم
```

```javascript
// JavaScript
__("charge", null, "mobile phone charge")
__("charge", null, "invoice line charge")
```

---

## 20.4 Finding Untranslated Strings

Frappe provides a bench command to extract strings that need translation:

```bash
bench --site mysite get-untranslated ar my_app/my_app/translations/ar_missing.csv
```

This outputs all strings used with `_()` in your app that don't yet have an Arabic translation.

---

## 20.5 When to Clear Cache vs Rebuild

| Change | Action needed |
|--------|--------------|
| Edit a `.csv` translation file | `bench --site mysite clear-cache` then refresh browser |
| Add `__()` to a JS file in `public/js/` | `bench build` |
| Add `_()` to a Python file | Just refresh browser |
| Add `_()` to a Jinja template | Just refresh browser |

---

## 20.6 Language Codes Reference

Common codes used in Frappe:

| Code | Language |
|------|----------|
| `ar` | Arabic |
| `de` | German |
| `es` | Spanish |
| `fr` | French |
| `hi` | Hindi |
| `id` | Indonesian |
| `it` | Italian |
| `ja` | Japanese |
| `ko` | Korean |
| `nl` | Dutch |
| `pt` | Portuguese |
| `ru` | Russian |
| `tr` | Turkish |
| `zh` | Chinese (Simplified) |

Find the full list in **Setup → Language** in your Frappe instance.

---

## 20.7 Complete Example

### App structure

```
my_app/
  my_app/
    translations/
      ar.csv
      es.csv
    doctype/
      asset/
        asset.py
```

### ar.csv

```csv
"source_string","translated_string","context"
"Asset","أصل",""
"Asset name is required","اسم الأصل مطلوب",""
"Active","نشط",""
"Inactive","غير نشط",""
"Generate Report","إنشاء تقرير",""
"Report generated successfully","تم إنشاء التقرير بنجاح",""
"charge","شحن","mobile phone charge"
"charge","رسوم","invoice line charge"
```

### asset.py

```python
from frappe import _
import frappe

class Asset(Document):
    def validate(self):
        if not self.asset_name:
            frappe.throw(_("Asset name is required"))

    def get_display_status(self):
        return _("Active") if self.is_active else _("Inactive")
```

### asset.js (client script)

```javascript
frappe.ui.form.on("Asset", {
    refresh(frm) {
        frm.add_custom_button(__("Generate Report"), () => {
            frappe.call({
                method: "my_app.asset.generate_report",
                args: { asset: frm.doc.name },
                callback(r) {
                    frappe.msgprint(__("Report generated successfully"));
                },
            });
        });
    },
});
```

### Testing

1. Go to **My Settings** → set Language to Arabic
2. Reload the page
3. Open an Asset form — labels should appear in Arabic
4. If not: `bench --site mysite clear-cache` and reload

---

## Summary

Frappe's i18n system is simple by design:

- Put CSV files in `my_app/translations/<lang_code>.csv`
- Wrap strings with `_()` in Python/Jinja and `__()` in JavaScript
- Use `context` to disambiguate words with multiple meanings
- No migration needed — translations load at runtime
- `bench clear-cache` is usually enough; `bench build` only for bundled JS

---

**Next Chapter**: Virtual DocTypes and Virtual Fields — working with data that doesn't live in the database.
