# -*- coding: utf-8 -*-
"""
Setup script for My Custom App
Chapter 3: Anatomy of an App

This script defines the package metadata and dependencies
for the custom Frappe application.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="my_custom_app",
    version="1.0.0",
    author="Mastering ERPNext Development",
    author_email="contact@mastering-erpnext.dev",
    description="Example custom application for ERPNext development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mastering-erpnext-dev/my_custom_app",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Frappe",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "factory-boy>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "my-custom-app-tool=my_custom_app.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "my_custom_app": [
            "public/**/*",
            "templates/**/*",
            "config/**/*",
            "patches/**/*",
            "fixtures/**/*",
        ],
    },
    zip_safe=False,
    keywords="frappe erpnext custom app development",
    project_urls={
        "Bug Reports": "https://github.com/mastering-erpnext-dev/my_custom_app/issues",
        "Source": "https://github.com/mastering-erpnext-dev/my_custom_app",
        "Documentation": "https://mastering-erpnext.dev/docs/my_custom_app",
    },
)
