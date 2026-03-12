# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "asset_management_app"
app_title = "Asset Management"
app_publisher = "Your Organization"
app_description = "Complete asset tracking and management system"
app_icon = "octicon octicon-package"
app_color = "blue"
app_email = "info@example.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/asset_management_app/css/asset_management_app.css"
# app_include_js = "/assets/asset_management_app/js/asset_management_app.js"

# include js, css files in header of web template
# web_include_css = "/assets/asset_management_app/css/asset_management_app.css"
# web_include_js = "/assets/asset_management_app/js/asset_management_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "asset_management_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "asset_management_app.install.before_install"
# after_install = "asset_management_app.install.after_install"

# Desk Notifications
# -------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "asset_management_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Asset": {
		"validate": "asset_management_app.asset_management.doctype.asset.asset.validate_asset",
		"on_update": "asset_management_app.asset_management.doctype.asset.asset.on_asset_update",
		"on_submit": "asset_management_app.asset_management.doctype.asset.asset.on_asset_submit",
		"on_cancel": "asset_management_app.asset_management.doctype.asset.asset.on_asset_cancel"
	},
	"Asset Assignment": {
		"on_submit": "asset_management_app.asset_management.doctype.asset_assignment.asset_assignment.on_assignment_submit",
		"on_cancel": "asset_management_app.asset_management.doctype.asset_assignment.asset_assignment.on_assignment_cancel"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"all": [],
	"daily": [
		"asset_management_app.tasks.daily.check_maintenance_due",
		"asset_management_app.tasks.daily.update_asset_values"
	],
	"hourly": [],
	"weekly": [
		"asset_management_app.tasks.weekly.generate_utilization_report"
	],
	"monthly": [
		"asset_management_app.tasks.monthly.calculate_depreciation"
	]
}

# Testing
# -------

# before_tests = "asset_management_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "asset_management_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "asset_management_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]
