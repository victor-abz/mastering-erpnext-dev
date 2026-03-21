from setuptools import setup, find_packages

setup(
    name="vendor_portal_app",
    version="0.0.1",
    description="REST API-based vendor portal for external integration",
    author="Your Organization",
    author_email="info@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=["frappe"],
)
