# Chapter 2: The Professional Dev Environment

## 🎯 Learning Objectives

By the end of this chapter, you will be able to:

- Set up Bench on Linux, macOS, and Windows WSL
- Master essential Bench commands for development
- Understand the Bench directory structure
- Configure Git integration for version control
- Manage multiple development sites
- Set up VS Code for optimal Frappe development

## 📚 Chapter Topics

### 2.1 Setting up Bench

#### System Requirements

**Minimum Requirements:**
- 4GB RAM (8GB recommended)
- 20GB disk space
- Python 3.8+
- Node.js 14+
- Redis server
- MariaDB 10.3+

**Supported Platforms:**
- Ubuntu 18.04+ / Debian 10+
- macOS 10.15+
- Windows 10+ with WSL2

#### Installation Methods

**Method 1: Automated Install (Recommended)**
```bash
# Install dependencies
curl -sL https://raw.githubusercontent.com/frappe/bench/develop/install.py | python3 - --production

# Create your first bench
bench init frappe-bench
cd frappe-bench
```

**Method 2: Manual Install**
```bash
# Clone bench repository
git clone https://github.com/frappe/bench bench-repo
sudo pip3 install -e bench-repo

# Initialize bench
bench init frappe-bench --frappe-path https://github.com/frappe/frappe
```

### 2.2 Bench Commands Deep Dive

#### Essential Commands

**Initialization:**
```bash
bench init <bench-name>              # Initialize new bench
bench new-app <app-name>             # Create new app
bench new-site <site-name>           # Create new site
bench use <site-name>                # Switch active site
```

**App Management:**
```bash
bench install-app <app-name>         # Install app on all sites
bench remove-app <app-name>          # Remove app
bench update-app <app-name>          # Update specific app
bench migrate                        # Run all pending migrations
```

**Site Management:**
```bash
bench --site <site-name> console     # Open Python console
bench --site <site-name> migrate     # Migrate specific site
bench --site <site-name> reinstall   # Reinstall site
bench --site <site-name> backup      # Backup site
```

**Development:**
```bash
bench start                          # Start development server
bench restart                        # Restart services
bench doctor                         # Check system health
bench --site <site-name> watch       # Watch for file changes
```

#### Advanced Commands

**Version Control:**
```bash
bench update                         # Update all apps
bench switch-to-branch <branch>      # Switch to specific branch
bench merge-upstream                  # Merge upstream changes
```

**Configuration:**
```bash
bench config dns_multitenant on      # Enable multi-tenancy
bench config serve_default_site on   # Serve default site
bench config redis_socketio          # Configure Redis
```

### 2.3 Understanding Bench Directory Structure

```
frappe-bench/
├── apps/                    # Installed applications
│   ├── frappe/             # Frappe framework
│   ├── erpnext/           # ERPNext application
│   └── my_custom_app/      # Your custom apps
├── sites/                  # Site configurations
│   ├── site1.local/       # Site-specific files
│   │   ├── private/       # Private files
│   │   ├── public/        # Public files
│   │   └── site_config.json
│   └── assets/            # Shared assets
├── config/                # Bench configuration
│   ├── bench_config.json
│   ├── nginx.conf
│   └── supervisor.conf
├── logs/                  # Application logs
├── env/                   # Python virtual environment
└── redis/                 # Redis configuration
```

#### Key Files Explained

**`bench_config.json`**
```json
{
    "auto_update": false,
    "background_workers": 1,
    "dns_multitenant": false,
    "frappe_user": "frappe",
    "live_site": "your-site.com",
    "mail_server": "smtp.gmail.com",
    "maintenance_mode": 0,
    "max_file_size": 10485760,
    "redis_cache": "redis://localhost:13000",
    "redis_queue": "redis://localhost:13001",
    "redis_socketio": "redis://localhost:13002",
    "restart_supervisor_on_update": false,
    "serve_default_site": true,
    "shallow_clone": true,
    "socketio_port": 9000,
    "update_bench_on_update": true,
    "webserver_port": 8000,
    "worker_count": 2
}
```

**`sites/site1.local/site_config.json`**
```json
{
    "db_name": "1bd2e3294da19198",
    "db_password": "your_password",
    "db_type": "mariadb",
    "enable_scheduler": true,
    "maintenance_mode": 0,
    "root_login": "administrator",
    "root_password": "your_admin_password"
}
```

### 2.4 Git Integration

#### Setting Up Version Control

**Initialize Git in Your App:**
```bash
cd apps/my_custom_app
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/my_custom_app.git
git push -u origin main
```

**Best Practices:**
```bash
# Create .gitignore
echo "env/" >> .gitignore
echo "sites/" >> .gitignore
echo "logs/" >> .gitignore

# Branch strategy
git checkout -b feature/new-doctype
git commit -am "Add new doctype"
git checkout main
git merge feature/new-doctype
```

### 2.5 Multiple Site Management

#### Development Workflow

**Create Development Sites:**
```bash
# Development site
bench new-site dev.local
bench --site dev.local install-app erpnext

# Testing site
bench new-site test.local
bench --site test.local install-app erpnext

# Staging site
bench new-site staging.local
bench --site staging.local install-app erpnext
```

**Site-Specific Configuration:**
```bash
# Switch between sites
bench use dev.local
bench use test.local

# Run commands on specific site
bench --site dev.local console
bench --site test.local migrate
```

#### Database Management

**Database Connections:**
```python
# In bench console
frappe.db.get_value('User', 'Administrator', 'email')
frappe.get_all('DocType', filters={'module': 'Core'})
```

**Backup and Restore:**
```bash
# Backup site
bench --site dev.local backup --with-files

# Restore from backup
bench --site dev.local restore /path/to/backup.sql
```

### 2.6 VS Code Configuration

#### Recommended Extensions

```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.flake8",
        "ms-python.black-formatter",
        "bradlc.vscode-tailwindcss",
        "formulahendry.auto-rename-tag",
        "ms-vscode.vscode-json",
        "redhat.vscode-yaml"
    ]
}
```

#### Workspace Settings

**`.vscode/settings.json`:**
```json
{
    "python.defaultInterpreterPath": "./env/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/node_modules": true,
        "**/env": true
    },
    "search.exclude": {
        "**/env": true,
        "**/node_modules": true
    }
}
```

**`.vscode/launch.json`:**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Bench Console",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/env/bin/bench",
            "args": ["--site", "dev.local", "console"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

#### Debugging Setup

**Python Debugging:**
```python
# In your custom app code
import frappe
import pdb; pdb.set_trace()  # Breakpoint

# Or use frappe logger
frappe.logger().debug("Debug message")
```

**JavaScript Debugging:**
```javascript
// In client scripts
console.log("Debug:", frm.doc);
debugger; // Browser breakpoint
```

## 🛠️ Practical Exercises

### Exercise 2.1: Complete Bench Setup

1. Install Bench on your system
2. Create a new bench
3. Install ERPNext
4. Create a development site
5. Verify all services are running

### Exercise 2.2: App Development Workflow

1. Create a new custom app
2. Initialize Git repository
3. Create a simple DocType
4. Commit and push changes
5. Test on multiple sites

### Exercise 2.3: VS Code Configuration

1. Install recommended extensions
2. Configure workspace settings
3. Set up debugging configuration
4. Test Python and JavaScript debugging

## 🚀 Common Issues & Solutions

### Installation Issues

**Problem:** Permission denied during installation
```bash
# Solution: Use virtual environment or proper permissions
sudo pip3 install frappe-bench
# OR
python3 -m venv venv
source venv/bin/activate
pip install frappe-bench
```

**Problem:** Redis connection failed
```bash
# Solution: Check Redis service
sudo systemctl status redis
sudo systemctl start redis
```

### Development Issues

**Problem:** Site not accessible
```bash
# Solution: Check bench status
bench doctor
bench restart
```

**Problem:** Migration failures
```bash
# Solution: Check for conflicts
bench --site dev.local migrate
# If fails, check logs
tail -f logs/worker.log
```

## 📖 Further Reading

- [Bench Documentation](https://frappeframework.com/docs/user/en/bench)
- [Development Setup Guide](https://frappeframework.com/docs/user/en/development/setup)
- [VS Code for Frappe Development](https://frappeframework.com/docs/user/en/development/vscode-setup)

## 🎯 Chapter Summary

A professional development environment is crucial for productive ERPNext development. Key takeaways:

- **Bench** is the command-line tool for managing Frappe applications
- **Multiple sites** allow proper development workflow
- **Git integration** ensures version control and collaboration
- **VS Code setup** provides optimal development experience
- **Understanding directory structure** helps in troubleshooting

---

**Next Chapter**: Understanding the anatomy of a Frappe application.
