from setuptools import setup, find_packages

setup(
    name="production_planning_app",
    version="0.0.1",
    description="Advanced production planning and scheduling system",
    author="Your Organization",
    author_email="info@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=["frappe"],
)
