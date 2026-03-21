from setuptools import setup, find_packages

setup(
    name="asset_management_app",
    version="0.0.1",
    description="Complete asset tracking and management system",
    author="Your Organization",
    author_email="info@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=["frappe"],
)
