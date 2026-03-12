# Asset Management System

Complete asset tracking and management application built with Frappe Framework.

## Features

### Core Functionality
- Asset registration and tracking
- Hierarchical asset categories
- Asset assignment workflow
- Depreciation calculation (Straight Line, Double Declining Balance)
- Maintenance scheduling and tracking
- Real-time dashboard with analytics
- Comprehensive utilization reports

### Asset Lifecycle Management
1. **Registration**: Create assets with purchase details, category, and depreciation settings
2. **Assignment**: Assign assets to employees or departments
3. **Maintenance**: Schedule and track preventive and corrective maintenance
4. **Depreciation**: Automatic calculation and tracking
5. **Disposal**: Record asset disposal and calculate gains/losses

### Automation
- Daily maintenance due notifications
- Automatic depreciation calculations
- Weekly utilization reports
- Monthly depreciation summaries
- Asset value updates

## Installation

```bash
# Navigate to your bench directory
cd ~/frappe-bench

# Get the app
bench get-app asset_management_app /path/to/projects/asset_management/asset_management_app

# Install on site
bench --site your-site.local install-app asset_management_app

# Run migrations
bench --site your-site.local migrate
```

## DocTypes

### 1. Asset
Main DocType for tracking assets.

**Key Fields:**
- Asset Name, Item Code, Serial Number
- Asset Category (Link to Asset Category)
- Purchase Date, Purchase Amount
- Depreciation Method, Useful Life
- Current Value, Accumulated Depreciation
- Status (Available, Assigned, Under Maintenance, Disposed)
- Location, Department, Custodian

**Controller Methods:**
- `validate_dates()`: Validate date logic
- `validate_amounts()`: Ensure positive amounts
- `calculate_depreciation()`: Calculate accumulated depreciation
- `calculate_current_value()`: Update current asset value

**API Methods:**
- `get_available_assets(asset_category)`: Get available assets
- `get_asset_utilization(asset_name, from_date, to_date)`: Calculate utilization

### 2. Asset Category
Hierarchical categorization of assets.

**Key Fields:**
- Category Name, Description
- Parent Category (for hierarchy)
- Is Group
- Depreciation Method, Useful Life (defaults for assets)
- Enable Maintenance, Maintenance Frequency
- Total Assets, Total Value (auto-calculated)

**Features:**
- Nested set model for hierarchy
- Default depreciation settings
- Automatic statistics updates

### 3. Asset Assignment
Track asset assignments to employees/departments.

**Key Fields:**
- Asset (Link)
- Assigned To (User)
- Department, Location
- From Date, To Date
- Assignment Status
- Return Condition

**Workflow:**
1. Create assignment
2. Submit to activate
3. Asset status changes to "Assigned"
4. On cancel, asset returns to "Available"

### 4. Asset Maintenance
Schedule and track maintenance activities.

**Key Fields:**
- Asset (Link)
- Maintenance Date, Next Maintenance Date
- Maintenance Type (Preventive, Corrective, Predictive, Emergency)
- Maintenance Status
- Performed By, Cost
- Description, Notes

**Features:**
- Automatic next maintenance date calculation
- Maintenance due notifications
- Cost tracking

## Dashboard

Access real-time analytics at `/app/asset-dashboard`

**Metrics:**
- Total assets and values
- Assets by category
- Assets by status
- Utilization rate
- Maintenance due count
- Depreciation trend (12 months)

**API Endpoint:**
```python
frappe.call('asset_management_app.asset_management.dashboard.asset_dashboard.get_dashboard_data')
```

## Reports

### Asset Utilization Report
Analyze asset usage patterns over time.

**Filters:**
- From Date, To Date (required)
- Asset Category (optional)

**Columns:**
- Asset, Asset Name, Category
- Status, Total Days
- Assigned Days, Utilization %
- Current Value

**Usage:**
```
Reports > Asset Utilization Report
```

## Scheduled Tasks

### Daily
- `check_maintenance_due()`: Send notifications for maintenance due in 7 days
- `update_asset_values()`: Recalculate current values

### Weekly
- `generate_utilization_report()`: Send utilization summary to Asset Managers

### Monthly
- `calculate_depreciation()`: Calculate monthly depreciation
- Send depreciation summary to finance team

## Permissions

### Asset Manager Role
- Full access to all DocTypes
- Can create, read, update, delete
- Receives notifications and reports

### Asset User Role
- Read access to assets
- Can create asset assignments
- Limited maintenance access

### Setup Roles
```bash
bench --site your-site.local add-role "Asset Manager"
bench --site your-site.local add-role "Asset User"
```

## Configuration

### 1. Setup Asset Categories
```
Asset Category > New
- Create hierarchy (e.g., IT Equipment > Laptops)
- Set depreciation defaults
- Enable maintenance if needed
```

### 2. Configure Scheduler
Scheduler events are defined in `hooks.py`:
```python
scheduler_events = {
    "daily": ["asset_management_app.tasks.daily.check_maintenance_due"],
    "weekly": ["asset_management_app.tasks.weekly.generate_utilization_report"],
    "monthly": ["asset_management_app.tasks.monthly.calculate_depreciation"]
}
```

### 3. Email Notifications
Configure email in `site_config.json`:
```json
{
    "mail_server": "smtp.example.com",
    "mail_port": 587,
    "use_tls": 1,
    "mail_login": "notifications@example.com",
    "mail_password": "password"
}
```

## API Examples

### Get Available Assets
```python
import frappe

assets = frappe.call(
    'asset_management_app.asset_management.doctype.asset.asset.get_available_assets',
    asset_category='Laptops'
)
```

### Calculate Utilization
```python
utilization = frappe.call(
    'asset_management_app.asset_management.doctype.asset.asset.get_asset_utilization',
    asset_name='ASSET-0001',
    from_date='2026-01-01',
    to_date='2026-03-31'
)

print(f"Utilization: {utilization['utilization_percentage']:.1f}%")
```

### Get Dashboard Data
```python
dashboard = frappe.call(
    'asset_management_app.asset_management.dashboard.asset_dashboard.get_dashboard_data'
)

print(f"Total Assets: {dashboard['summary']['total_assets']}")
print(f"Utilization Rate: {dashboard['utilization']['utilization_rate']:.1f}%")
```

## Testing

Run tests:
```bash
bench --site your-site.local run-tests --app asset_management_app
```

Test specific DocType:
```bash
bench --site your-site.local run-tests --doctype "Asset"
```

## Troubleshooting

### Assets not depreciating
- Check if depreciation method is set
- Verify useful life is configured
- Ensure scheduler is running: `bench enable-scheduler`

### Maintenance notifications not sending
- Verify email configuration
- Check scheduler status
- Review error logs: `bench --site your-site.local console`

### Dashboard not loading
- Clear cache: `bench --site your-site.local clear-cache`
- Check browser console for errors
- Verify permissions for Asset Manager role

## Best Practices

1. **Asset Categories**: Create a logical hierarchy before adding assets
2. **Depreciation**: Set category-level defaults to avoid repetition
3. **Maintenance**: Enable for categories that require regular servicing
4. **Assignments**: Always use the Assignment DocType for tracking
5. **Reports**: Run utilization reports monthly for insights

## Extending the App

### Add Custom Fields
```python
# In fixtures or custom script
frappe.get_doc({
    'doctype': 'Custom Field',
    'dt': 'Asset',
    'fieldname': 'warranty_expiry',
    'fieldtype': 'Date',
    'label': 'Warranty Expiry'
}).insert()
```

### Add Custom Report
Create new report in `asset_management/report/`

### Add Workflow
Create workflow for asset approval process

## Support

For issues and questions:
- GitHub Issues: [repository-url]
- Frappe Forum: https://discuss.frappe.io
- Documentation: See chapter-11-asset-management/README.md

## License

MIT License - See LICENSE file

---

**Built with Frappe Framework** | Chapter 11: Real-World Projects
