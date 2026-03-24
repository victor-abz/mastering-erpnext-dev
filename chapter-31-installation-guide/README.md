# Chapter 31: Installation Guide — Frappe, ERPNext & Docker

## Overview

This chapter covers all installation methods: bare-metal Ubuntu setup, Docker production deployment, Docker development containers (devcontainers), and app boilerplate initialization.

---

## 1. Bare-Metal Installation (Ubuntu)

### Prerequisites

```bash
# 1. Update system
sudo apt-get update -y
sudo apt-get upgrade -y
sudo reboot

# 2. Install Git
sudo apt-get install git

# 3. Install Python
sudo apt-get install python3-dev python3.10-dev python3-setuptools python3-pip python3-distutils
sudo apt-get install python3.10-venv
sudo apt-get install software-properties-common

# 4. Install MariaDB
sudo apt install mariadb-server mariadb-client
sudo mysql_secure_installation
```

When running `mysql_secure_installation`:
```
Enter current password for root: (leave empty)
Switch to unix_socket authentication [Y/n]: Y
Change the root password? [Y/n]: Y
Remove anonymous users? [Y/n]: Y
Disallow root login remotely? [Y/n]: N
Remove test database? [Y/n]: Y
Reload privilege tables? [Y/n]: Y
```

```bash
# 5. Configure MariaDB for UTF8
sudo nano /etc/mysql/my.cnf
```

Add at the end of `/etc/mysql/my.cnf`:
```ini
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4
```

```bash
sudo service mysql restart

# 6. Install Redis
sudo apt-get install redis-server

# 7. Install other dependencies
sudo apt-get install xvfb libfontconfig wkhtmltopdf
sudo apt-get install libmysqlclient-dev
sudo apt install curl

# 8. Install Node.js via NVM
curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
source ~/.profile
nvm install 18

# 9. Install NPM and Yarn
sudo apt-get install npm
sudo npm install -g yarn

# 10. Install Frappe Bench
sudo pip3 install frappe-bench
```

### Initialize Bench and Create Site

```bash
# Initialize bench (replace version-16 with your target version)
bench init --frappe-branch version-16 frappe-bench
cd /home/frappe-user/frappe-bench

# Create new site
bench new-site mysite.local

# Enable scheduler
bench --site mysite.local enable-scheduler

# Disable maintenance mode
bench --site mysite.local set-maintenance-mode off

# Enable server scripts
bench --site mysite.local set-config server_script_enabled true

# Enable developer mode (development only)
bench set-config -g developer_mode true

# Add site to hosts (local dev)
bench --site mysite.local add-to-hosts

# Start server
bench start
```

Access at: `http://mysite.local:8000` or `http://localhost:8000`

### Install ERPNext

```bash
bench get-app erpnext --branch version-16
bench --site mysite.local install-app erpnext
bench --site mysite.local migrate
```

---

## 2. Docker Production Deployment (frappe_docker)

### Quick Start with pwd.yml

```bash
# Clone frappe_docker
git clone https://github.com/frappe/frappe_docker
cd frappe_docker

# Start with the default configuration
docker compose -f pwd.yml up -d

# Monitor site creation
docker logs frappe_docker-create-site-1 -f
```

Access at: `http://localhost:8080`

### Custom App Docker Image

**Step 1: Create apps.json**

```json
[
  {
    "url": "https://github.com/frappe/erpnext",
    "branch": "version-16"
  },
  {
    "url": "https://github.com/your-username/your-custom-app",
    "branch": "main"
  }
]
```

For private repos:
```json
[
  {
    "url": "https://YOUR_PAT@github.com/your-org/private-app.git",
    "branch": "main"
  }
]
```

**Step 2: Build the image**

```bash
# Encode apps.json
export APPS_JSON_BASE64=$(base64 -w 0 apps.json)

# Verify encoding
echo -n ${APPS_JSON_BASE64} | base64 -d > apps-test.json
cat apps-test.json

# Build image
docker build \
  --no-cache \
  --progress=plain \
  --build-arg FRAPPE_BRANCH=version-16 \
  --build-arg APPS_JSON_BASE64=$APPS_JSON_BASE64 \
  --file images/layered/Containerfile \
  --tag your-dockerhub-username/frappe-custom:latest \
  .
```

**Step 3: Push to Docker Hub**

```bash
# Login (use Personal Access Token, not password)
docker login -u your-dockerhub-username

# Push
docker push your-dockerhub-username/frappe-custom:latest
```

**Step 4: Run with custom image**

Edit `pwd.yml` — replace all `frappe/erpnext:v16.x.x` with your image:
```yaml
image: your-dockerhub-username/frappe-custom:latest
```

Update the site creation command:
```yaml
command: >-
  --install-app erpnext --install-app your_custom_app
```

```bash
docker compose -f pwd.yml up -d
```

---

## 3. Docker Compose Deep Dive

### Understanding the Frappe Stack

Frappe requires these services working together:

```
┌─────────────────────────────────────────────────────┐
│  frappe_docker services                             │
├─────────────────────────────────────────────────────┤
│  frontend    → Nginx (port 8080) + static files     │
│  backend     → Gunicorn (Python app server)         │
│  websocket   → Socket.IO (real-time)                │
│  queue-short → Background worker (short jobs)       │
│  queue-long  → Background worker (long jobs)        │
│  scheduler   → Cron-like task scheduler             │
│  db          → MariaDB                              │
│  redis-cache → Redis (caching)                      │
│  redis-queue → Redis (job queue)                    │
└─────────────────────────────────────────────────────┘
```

### Minimal docker-compose.yml

```yaml
version: "3.8"

x-customizable-image: &customizable_image
  image: ${CUSTOM_IMAGE:-frappe/erpnext}:${CUSTOM_TAG:-v16.0.0}
  restart: ${RESTART_POLICY:-unless-stopped}

x-backend-defaults: &backend_defaults
  <<: *customizable_image
  volumes:
    - sites:/home/frappe/frappe-bench/sites
    - logs:/home/frappe/frappe-bench/logs

services:
  configurator:
    <<: *backend_defaults
    restart: on-failure
    entrypoint: ["bash", "-c"]
    command: >
      ls -1 apps > sites/apps.txt;
      bench set-config -g db_host $DB_HOST;
      bench set-config -g redis_cache "redis://$REDIS_CACHE";
      bench set-config -g redis_queue "redis://$REDIS_QUEUE";
      bench set-config -g redis_socketio "redis://$REDIS_QUEUE";
    environment:
      DB_HOST: ${DB_HOST:-db}
      REDIS_CACHE: ${REDIS_CACHE:-redis-cache:6379}
      REDIS_QUEUE: ${REDIS_QUEUE:-redis-queue:6379}
    depends_on:
      db:
        condition: service_healthy

  backend:
    <<: *backend_defaults
    depends_on:
      configurator:
        condition: service_completed_successfully

  frontend:
    <<: *customizable_image
    command: nginx-entrypoint.sh
    environment:
      BACKEND: backend:8000
      SOCKETIO: websocket:9000
      FRAPPE_SITE_NAME_HEADER: ${FRAPPE_SITE_NAME_HEADER:-$$host}
    volumes:
      - sites:/home/frappe/frappe-bench/sites
    ports:
      - "${HTTP_PUBLISH_PORT:-8080}:8080"
    depends_on:
      - backend
      - websocket

  websocket:
    <<: *backend_defaults
    command: node /home/frappe/frappe-bench/apps/frappe/socketio.js

  queue-short:
    <<: *backend_defaults
    command: bench worker --queue short,default

  queue-long:
    <<: *backend_defaults
    command: bench worker --queue long,default,short

  scheduler:
    <<: *backend_defaults
    command: bench schedule

  db:
    image: mariadb:10.6
    healthcheck:
      test: mysqladmin ping -h localhost --password=${DB_PASSWORD:-123}
      interval: 1s
      retries: 20
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD:-123}
    volumes:
      - db-data:/var/lib/mysql

  redis-cache:
    image: redis:6.2-alpine

  redis-queue:
    image: redis:6.2-alpine

volumes:
  db-data:
  sites:
  logs:
```

### Key Docker Compose Concepts

**Dependency conditions:**
- `service_started` — container started (default)
- `service_healthy` — healthcheck passed
- `service_completed_successfully` — ran and exited 0

**Restart policies:**
- `unless-stopped` — restart unless manually stopped (recommended)
- `on-failure` — restart only on failure (for one-time jobs like configurator)
- `always` — always restart

**Volume types:**
- Named volumes (`sites:`) — Docker-managed, portable, for production
- Bind mounts (`./sites:/path`) — host directory, for development

---

## 4. Dev Containers (VS Code)

Dev Containers let you develop inside a Docker container with VS Code, giving everyone the same environment.

### Setup

```bash
# 1. Clone frappe_docker
git clone https://github.com/frappe/frappe_docker.git
cd frappe_docker

# 2. Copy devcontainer config
cp -R devcontainer-example .devcontainer
cp -R development/vscode-example development/.vscode

# 3. Open in VS Code
code .
```

In VS Code:
1. Install extension: `ms-vscode-remote.remote-containers`
2. Press `Ctrl+Shift+P` → `Dev Containers: Reopen in Container`
3. Wait 5-10 minutes for first build

### Inside the Container

```bash
# Initialize bench
bench init --skip-redis-config-generation frappe-bench
cd frappe-bench

# Configure connections
bench set-config -g db_host mariadb
bench set-config -g redis_cache redis://redis-cache:6379
bench set-config -g redis_queue redis://redis-queue:6379
bench set-config -g redis_socketio redis://redis-queue:6379

# Create site
bench new-site \
  --db-root-password 123 \
  --admin-password admin \
  --mariadb-user-host-login-scope=% \
  mysite.localhost

# Install ERPNext
bench get-app erpnext
bench --site mysite.localhost install-app erpnext

# Start server
bench start
```

Access at: `http://development.localhost:8000`

### devcontainer.json Reference

```json
{
  "name": "Frappe Bench",
  "dockerComposeFile": "./docker-compose.yml",
  "service": "frappe",
  "workspaceFolder": "/workspace/development",
  "shutdownAction": "stopCompose",
  "remoteUser": "frappe",
  "forwardPorts": [8000, 9000, 6787],
  "mounts": [
    "source=${localEnv:HOME}${localEnv:USERPROFILE}/.ssh,target=/home/frappe/.ssh,type=bind,consistency=cached"
  ],
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-vscode.live-server",
        "mtxr.sqltools",
        "visualstudioexptteam.vscodeintellicode"
      ],
      "settings": {
        "terminal.integrated.defaultProfile.linux": "bash",
        "debug.node.autoAttach": "disabled"
      }
    }
  }
}
```

### Common Dev Container Errors

**`NameError: name 'null' is not defined`**
```bash
bench clear-cache
# Or try a different browser
```

**`Cannot find module 'superagent'`**
```bash
bench setup requirements
```

**`ValueError: id must not contain ":"`**
```bash
# Update to latest Frappe version
bench update --reset
```

---

## 5. App Boilerplate Setup

### Create New App

```bash
bench new-app your-app-name
# Fill in: title, description, publisher, email, license
```

### Professional App Structure

```
your_app/
├── your_app/
│   ├── __init__.py          # Version + constants import
│   ├── hooks.py             # Frappe hooks
│   ├── constants.py         # App constants
│   ├── modules.txt          # Module list
│   ├── patches.txt          # Migration patches
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── main.py
│   ├── public/
│   │   ├── js/
│   │   ├── css/
│   │   └── images/branding/
│   │       ├── logo.png
│   │       └── favicon.png
│   ├── templates/
│   ├── translations/
│   │   └── ar.csv
│   └── utils/
│       └── install.py
├── setup.py
├── requirements.txt
├── CHANGELOG.md
└── README.md
```

### `__init__.py`

```python
from .constants import *

__version__ = "0.1.0"
```

### `constants.py`

```python
APP_NAME = "Your App Name"
APP_VERSION = "0.1.0"

ERRORS = {
    "no_permission": "Insufficient permissions",
    "not_found": "Record not found",
}

DEFAULT_PAGE_SIZE = 20
MAX_UPLOAD_SIZE = 10485760  # 10MB
API_VERSION = "v1"
```

### `setup.py`

```python
from setuptools import setup, find_packages
from your_app import __version__ as version

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="your_app",
    version=version,
    description="Your app description",
    author="Your Organization",
    author_email="your@email.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
```

### `utils/install.py`

```python
import frappe

def after_install():
    set_app_logo()
    set_system_settings()
    set_navbar_settings()

def after_migrate():
    set_app_logo()
    set_system_settings()

def set_app_logo():
    app_logo = frappe.get_hooks("app_logo_url")[-1]
    frappe.db.set_single_value("Navbar Settings", "app_logo", app_logo)

def set_system_settings():
    settings = frappe.get_doc("System Settings")
    settings.session_expiry = "12:00"
    settings.save()

def set_navbar_settings():
    settings = frappe.get_doc("Navbar Settings")
    settings.logo_width = "35"
    settings.save()
```

### `hooks.py` branding section

```python
app_logo_url = "/assets/your_app/images/branding/logo.png"

website_context = {
    "favicon": "/assets/your_app/images/branding/favicon.png",
    "splash_image": "/assets/your_app/images/branding/logo.png",
}

after_install = "your_app.utils.install.after_install"
after_migrate = "your_app.utils.install.after_migrate"
```

### Git Workflow

```bash
# Initial commit to dev branch
git add .
git commit -m "feat: initial project setup"
git branch -M dev
git remote add upstream https://github.com/your-org/your-app.git
git push upstream dev

# Create staging branch
git checkout -b staging
git push upstream staging
```

**Branch strategy:**
```
dev → staging → main
```
- `dev`: active development
- `staging`: QA/testing
- `main`: production-ready

---

## 6. Disabling Onboarding

New users often get redirected to onboarding even when disabled in System Settings. This is because Frappe has multiple onboarding layers.

### Complete Disable

```python
# In your app's install.py or a patch
import frappe

def disable_all_onboarding():
    # 1. System-wide toggle
    frappe.db.set_single_value("System Settings", "enable_onboarding", 0)

    # 2. Clear per-user status
    users = frappe.get_all("User", filters={"enabled": 1}, pluck="name")
    for user in users:
        frappe.db.set_value("User", user, "onboarding_status", "{}")
        frappe.cache.hdel("bootinfo", user)

    # 3. Mark all module onboardings complete
    for module in frappe.get_all("Module Onboarding", pluck="name"):
        frappe.db.set_value("Module Onboarding", module, "is_complete", 1)

    # 4. Disable form tours
    for tour in frappe.get_all("Form Tour", pluck="name"):
        frappe.db.set_value("Form Tour", tour, "ui_tour", 0)

    frappe.db.commit()
```

### Hook for New Users

```python
# hooks.py
doc_events = {
    "User": {
        "after_insert": "your_app.utils.user.disable_user_onboarding"
    }
}
```

```python
# your_app/utils/user.py
def disable_user_onboarding(doc, method):
    if not doc.enabled:
        return
    frappe.db.set_value("User", doc.name, "onboarding_status", "{}")
    frappe.cache.hdel("bootinfo", doc.name)
    frappe.db.commit()
```

### SQL Approach

```sql
-- Disable system onboarding
UPDATE `tabSingles`
SET `value` = '0'
WHERE `doctype` = 'System Settings' AND `field` = 'enable_onboarding';

-- Clear all user onboarding status
UPDATE `tabUser` SET `onboarding_status` = '{}' WHERE `enabled` = 1;

-- Mark all module onboardings complete
UPDATE `tabModule Onboarding` SET `is_complete` = 1;
```

---

## 7. After Container Restart (frappe_docker)

Apps and Python paths can be lost after container restart. Fix with:

```powershell
# Windows PowerShell (fix-after-restart.ps1)
docker exec -u root frappe_docker-backend-1 `
    pip install -e /home/frappe/frappe-bench/apps/your_app

docker exec frappe_docker-backend-1 `
    bench --site frontend migrate

docker restart frappe_docker-backend-1 frappe_docker-queue-short-1 frappe_docker-queue-long-1
```

---

## Quick Reference

| Task | Command |
|---|---|
| Create site | `bench new-site mysite.local` |
| Install app | `bench --site mysite install-app appname` |
| Migrate | `bench --site mysite migrate` |
| Clear cache | `bench --site mysite clear-cache` |
| Build assets | `bench build` |
| Start dev server | `bench start` |
| Run tests | `bench --site mysite run-tests appname` |
| Backup | `bench --site mysite backup` |
| Console | `bench --site mysite console` |
| Enable dev mode | `bench set-config -g developer_mode true` |
| List sites | `bench list-sites` |
| Drop site | `bench drop-site mysite.local` |


---

## 📌 Addendum: Platform-Specific Installation Guides

### Docker Dev Setup (Recommended for All Platforms)

Docker gives you a clean, reproducible environment without installing Python, Node, Redis, and MariaDB on your machine.

**Prerequisites:**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)
- VS Code with [Remote Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- Git

**Quick Start:**

```bash
# Step 1: Clone and setup
git clone https://github.com/frappe/frappe_docker.git
cd frappe_docker
cp -R devcontainer-example .devcontainer
cp -R development/vscode-example development/.vscode
code .

# Step 2: Open in Container
# Press Ctrl+Shift+P → "Dev Containers: Reopen in Container"
# Wait 5-10 minutes for first build

# Step 3: Initialize bench (inside container terminal)
bench init --skip-redis-config-generation frappe-bench
cd frappe-bench

# Step 4: Configure database & Redis
bench set-config -g db_host mariadb
bench set-config -g redis_cache redis://redis-cache:6379
bench set-config -g redis_queue redis://redis-queue:6379
bench set-config -g redis_socketio redis://redis-queue:6379

# Step 5: Create site
bench new-site --db-root-password 123 --admin-password admin \
  --mariadb-user-host-login-scope=% your_site_name.localhost

# Step 6: Start server
bench start
# Access at: http://development.localhost:8000
```

**Daily Workflow:**
- Start: Open VS Code → `Ctrl+Shift+P` → "Dev Containers: Reopen in Container" → `bench start`
- Stop: `Ctrl+Shift+P` → "Dev Containers: Reopen Folder Locally"

**Common Docker Errors:**

```bash
# NameError: name 'null' is not defined
bench clear-cache

# Missing module (e.g., "Cannot find module 'superagent'")
bench setup requirements

# ValueError: id must not contain ":"
# Fix in frappe/utils/backgroundjobs.py:
def create_job_id(job_id=None):
    if not job_id:
        job_id = str(uuid4())
    else:
        job_id = job_id.replace(":", "|")
    return f"{frappe.local.site}||{job_id}"
```

---

### Linux Installation (Ubuntu/Debian)

> Important: Install the exact versions of Python, Node, MariaDB, and frappe-bench that your team uses.

```bash
# 1. Update packages
sudo apt-get update -y && sudo apt-get upgrade -y

# 2. Install Git
sudo apt-get install git

# 3. Install Python
sudo apt-get install python3-dev python3.10-dev python3-setuptools python3-pip python3-distutils

# 4. Install Python virtual environment
sudo apt-get install python3.10-venv

# 5. Install MariaDB
sudo apt install mariadb-server mariadb-client
sudo mysql_secure_installation

# 6. Configure MariaDB (add to /etc/mysql/my.cnf)
sudo nano /etc/mysql/my.cnf
```

Add at end of file:
```ini
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4
```

```bash
sudo service mysql restart

# 7. Install Redis
sudo apt-get install redis-server

# 8. Install other dependencies
sudo apt-get install xvfb libfontconfig wkhtmltopdf
sudo apt-get install libmysqlclient-dev

# 9. Install Node.js via nvm
curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
source ~/.profile
nvm install 18

# 10. Install yarn
sudo npm install -g yarn

# 11. Install Frappe Bench (use pipx — recommended)
sudo apt install pipx
pipx ensurepath
pipx install frappe-bench

# 12. Initialize bench
bench init --frappe-branch version-16 frappe-bench
cd frappe-bench

# 13. Create site
bench new-site your-site-name.localhost

# 14. Configure site
bench --site your-site-name.localhost enable-scheduler
bench --site your-site-name.localhost set-maintenance-mode off
bench --site your-site-name.localhost set-config server_script_enabled true
bench set-config -g developer_mode true

# 15. Add to hosts and start
bench --site your-site-name.localhost add-to-hosts
bench start
```

---

### macOS Installation (Intel)

```bash
# 1. Install Xcode & Homebrew
xcode-select --install
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install dependencies
brew update
brew install git
brew install python@3.11
brew install node@18
brew install yarn
brew install redis@6.2
brew install mariadb@10.6
brew install pkg-config swig fontconfig

# 3. Set PATH (add to ~/.zshrc)
export PATH="/usr/local/opt/python@3.11/bin:$PATH"
export PATH="/usr/local/opt/mariadb@10.6/bin:$PATH"
export PKG_CONFIG_PATH="/usr/local/opt/mariadb@10.6/lib/pkgconfig:$PKG_CONFIG_PATH"

# 4. Install pipx and bench
python3.11 -m pip install --user pipx
python3.11 -m pipx ensurepath
pipx install frappe-bench --python python3.11

# 5. Install wkhtmltopdf
curl -L --http1.1 -O "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-2/wkhtmltox-0.12.6-2.macos-cocoa.pkg"
sudo installer -pkg wkhtmltox-0.12.6-2.macos-cocoa.pkg -target /

# 6. Start services
brew services start redis@6.2
brew services start mariadb@10.6

# 7. Configure MariaDB (add to /usr/local/etc/my.cnf)
nano /usr/local/etc/my.cnf
```

Add:
```ini
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
bind-address = 127.0.0.1

[mysql]
default-character-set = utf8mb4
```

```bash
brew services restart mariadb@10.6

# 8. Initialize bench and create site
bench init --frappe-branch version-16 frappe-bench
cd frappe-bench
bench new-site your-site-name.localhost
bench --site your-site-name.localhost enable-scheduler
bench set-config -g developer_mode true
bench --site your-site-name.localhost add-to-hosts
bench start
```

---

### Windows Installation (via WSL2)

Frappe doesn't run natively on Windows. Use WSL2 (Windows Subsystem for Linux) to get a Linux environment.

**Step 1: Enable WSL2**

```powershell
# Run as Administrator
wsl --install
# OR manually:
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
```

Fix Hyper-V if needed:
```powershell
bcdedit /set hypervisorlaunchtype auto
# Restart computer
```

**Step 2: Install Ubuntu**

```powershell
wsl --install -d Ubuntu-24.04
# Follow prompts to create username and password
```

| ERPNext Version | Ubuntu | Python | Node.js |
|-----------------|--------|--------|---------|
| v13.x | 20.04 | 3.8 | 14/16 |
| v14.x | 22.04 | 3.10 | 16/18 |
| v15.x+ | 24.04 | 3.12 | 18/20 |

**Step 3: Fix WSL2 Internet Access**

```powershell
# In CMD (not PowerShell):
echo [wsl2]> %USERPROFILE%\.wslconfig
echo dnsTunneling=true>> %USERPROFILE%\.wslconfig
echo networkingMode=mirrored>> %USERPROFILE%\.wslconfig
wsl --shutdown
wsl -d Ubuntu-24.04
```

**Step 4: Install Frappe in WSL2**

Open Ubuntu terminal and follow the Linux installation steps above.

**Step 5: Connect VS Code to WSL2**

```bash
# Install Remote-WSL extension
code --install-extension ms-vscode-remote.remote-wsl

# Open project in WSL
wsl -d Ubuntu-24.04
cd ~/frappe-bench
code .
```

Then from VS Code: `Ctrl+Shift+P` → "Connect to WSL using Distro" → Ubuntu-24.04

**Step 6: Fix "No process manager found" error**

```bash
pipx install honcho
pipx inject frappe-bench honcho
bench start
```

---

### Version Compatibility Matrix

| ERPNext | Frappe | Python | Node | MariaDB |
|---------|--------|--------|------|---------|
| v16.x | v16.x | 3.11+ | 18/20 | 10.6+ |
| v15.x | v15.x | 3.11 | 18 | 10.6 |
| v14.x | v14.x | 3.10 | 16/18 | 10.3+ |
| v13.x | v13.x | 3.8 | 14 | 10.3 |

### Post-Installation Checklist

```bash
# Install ERPNext on your site
bench get-app erpnext
bench --site your-site.localhost install-app erpnext

# Run migrations
bench --site your-site.localhost migrate

# Enable developer mode (development only)
bench set-config -g developer_mode true

# Verify installation
bench --site your-site.localhost doctor
```

### Useful bench Commands

```bash
bench list-sites                          # List all sites
bench use your-site.localhost             # Set default site
bench --site your-site.localhost console  # Python console
bench --site your-site.localhost migrate  # Run migrations
bench --site your-site.localhost backup   # Backup site
bench update --reset                      # Update all apps
bench restart                             # Restart all services
bench clear-cache                         # Clear Redis cache
```


---

## Addendum: Source Article Insights

### Manual Installation on Ubuntu/Debian

This is the standard bare-metal installation for a development or production server.

```bash
# 1. Update system
sudo apt-get update -y && sudo apt-get upgrade -y
sudo reboot

# 2. Install system dependencies
sudo apt-get install -y git
sudo apt-get install -y python3-dev python3.10-dev python3-setuptools python3-pip python3-distutils
sudo apt-get install -y python3.10-venv
sudo apt-get install -y software-properties-common

# 3. Install MariaDB
sudo apt install -y mariadb-server mariadb-client
sudo mysql_secure_installation
# Prompts:
#   Enter current password: (leave empty)
#   Switch to unix_socket authentication: Y
#   Change root password: Y
#   Remove anonymous users: Y
#   Disallow root login remotely: N
#   Remove test database: Y
#   Reload privilege tables: Y

# 4. Configure MariaDB for utf8mb4
sudo nano /etc/mysql/my.cnf
# Add at the end:
# [mysqld]
# character-set-client-handshake = FALSE
# character-set-server = utf8mb4
# collation-server = utf8mb4_unicode_ci
# [mysql]
# default-character-set = utf8mb4

sudo service mysql restart

# 5. Install Redis
sudo apt-get install -y redis-server

# 6. Install wkhtmltopdf and other packages
sudo apt-get install -y xvfb libfontconfig wkhtmltopdf
sudo apt-get install -y libmysqlclient-dev
sudo apt install -y curl

# 7. Install Node.js via nvm
curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
source ~/.profile
nvm install 18

# 8. Install npm and yarn
sudo apt-get install -y npm
sudo npm install -g yarn

# 9. Install Frappe Bench
sudo pip3 install frappe-bench

# 10. Initialize bench (replace version and folder name)
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench

# 11. Create a new site
bench new-site mysite.localhost

# 12. Configure the site
bench --site mysite.localhost enable-scheduler
bench --site mysite.localhost set-maintenance-mode off
bench --site mysite.localhost set-config server_script_enabled true

# 13. Enable developer mode (dev machines only)
bench set-config -g developer_mode true

# 14. Add site to /etc/hosts (local dev)
bench --site mysite.localhost add-to-hosts

# 15. Start the server
bench start
# Access at http://mysite.localhost:8000
```

---

### Docker-Based Development Environment

The fastest way to get started — no local Python/Node/MariaDB installation required.

**Prerequisites:** Docker Desktop, VS Code, Git

```bash
# 1. Clone frappe_docker
git clone https://github.com/frappe/frappe_docker.git
cd frappe_docker

# 2. Copy dev container config
cp -R devcontainer-example .devcontainer
cp -R development/vscode-example development/.vscode

# 3. Open in VS Code
code .
```

**In VS Code:**
1. Install extension: `ms-vscode-remote.remote-containers`
2. Press `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"
3. Wait 5–10 minutes for first build

**Inside the container terminal:**

```bash
# Initialize bench
bench init --skip-redis-config-generation frappe-bench
cd frappe-bench

# Point to Docker services (not localhost)
bench set-config -g db_host mariadb
bench set-config -g redis_cache redis://redis-cache:6379
bench set-config -g redis_queue redis://redis-queue:6379
bench set-config -g redis_socketio redis://redis-queue:6379

# Verify config
cat sites/common_site_config.json
# Should show: db_host, redis_cache, redis_queue, redis_socketio

# Create site
bench new-site \
  --db-root-password 123 \
  --admin-password admin \
  --mariadb-user-host-login-scope=% \
  development.localhost

# Start server
bench start
# Access at http://development.localhost:8000
```

**Daily workflow:**
- Start: `Ctrl+Shift+P` → "Dev Containers: Reopen in Container" → `bench start`
- Stop: `Ctrl+Shift+P` → "Dev Containers: Reopen Folder Locally"

---

### Installing ERPNext and Custom Apps

```bash
# Install ERPNext
bench get-app --branch version-15 erpnext
bench --site mysite.localhost install-app erpnext

# Install a custom app from GitHub
bench get-app https://github.com/myorg/my-custom-app.git --branch main
bench --site mysite.localhost install-app my_custom_app

# List installed apps
bench list-apps

# Migrate after installing
bench --site mysite.localhost migrate
```

---

### Docker Image with Custom App

For deploying your custom app via Docker:

```bash
# 1. Create apps.json
cat > apps.json << 'EOF'
[
  {"url": "https://github.com/frappe/erpnext", "branch": "version-15"},
  {"url": "https://github.com/myorg/my-custom-app", "branch": "main"}
]
EOF

# 2. Build custom image
export APPS_JSON_BASE64=$(base64 -w 0 apps.json)

git clone https://github.com/frappe/frappe_docker
cd frappe_docker

docker build \
  --build-arg FRAPPE_BRANCH=version-15 \
  --build-arg APPS_JSON_BASE64=$APPS_JSON_BASE64 \
  --file images/layered/Containerfile \
  --tag myorg/my-frappe-app:latest \
  .

# 3. Run with Docker Compose
# Edit pwd.yml: replace frappe/erpnext:v15.x.x with myorg/my-frappe-app:latest
# Also update install-app command to include your app name

docker compose -f pwd.yml up -d
docker logs frappe_container-create-site-1 -f
```

---

### Common Post-Installation Issues

**NameError: name 'null' is not defined** (after switching branches):
```bash
bench clear-cache
```

**Missing Node module (e.g., "Cannot find module 'superagent'"):**
```bash
bench setup requirements
```

**ValueError: id must not contain ":"** (older Frappe versions):
```bash
# Best fix: update Frappe
bench update --frappe
# Or apply the patch manually in frappe/utils/backgroundjobs.py
```

**Site not accessible after setup:**
```bash
# Check if site is set as default
cat sites/currentsite.txt

# Set default site
bench use mysite.localhost

# Check Nginx/Supervisor status (production)
sudo supervisorctl status
sudo systemctl status nginx
```
