# -*- coding: utf-8 -*-
"""
My Custom App - Example application for Mastering ERPNext Development
Chapter 3: Anatomy of an App

This app demonstrates the complete structure and functionality
of a Frappe application.
"""

__version__ = "1.0.0"
__author__ = "Mastering ERPNext Development"
__license__ = "MIT"
__description__ = "Example custom application for ERPNext development"

# App configuration
app_name = "my_custom_app"
app_title = "My Custom App"
app_publisher = "Mastering ERPNext Development"
app_description = "Example application demonstrating Frappe app structure"
app_icon = "octicon octicon-package"
app_color = "grey"
app_version = "1.0.0"
app_homepage = "https://github.com/mastering-erpnext-dev/my_custom_app"

# Include in desktop
includes_in_desktop = True

# Required apps (dependencies)
required_apps = ["frappe"]

# App license and copyright
app_license = "MIT"
app_copyright = "Copyright 2026, Mastering ERPNext Development"
