#!/bin/bash
# Production Setup Script
# Chapter 17: Production Pipeline

set -e

echo "=== ERPNext Production Setup ==="

# Variables
BENCH_USER="frappe"
BENCH_PATH="/home/$BENCH_USER/frappe-bench"
SITE_NAME="$1"

if [ -z "$SITE_NAME" ]; then
    echo "Usage: $0 <site-name>"
    exit 1
fi

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
echo "Installing dependencies..."
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-venv \
    redis-server \
    mariadb-server \
    nginx \
    supervisor \
    git \
    curl \
    wget

# Install Node.js
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install yarn
echo "Installing yarn..."
sudo npm install -g yarn

# Create frappe user
if ! id "$BENCH_USER" &>/dev/null; then
    echo "Creating frappe user..."
    sudo adduser --disabled-password --gecos "" $BENCH_USER
fi

# Install bench
echo "Installing bench..."
sudo -u $BENCH_USER pip3 install frappe-bench

# Initialize bench
if [ ! -d "$BENCH_PATH" ]; then
    echo "Initializing bench..."
    sudo -u $BENCH_USER bench init $BENCH_PATH --frappe-branch version-15
fi

cd $BENCH_PATH

# Create site
echo "Creating site: $SITE_NAME..."
sudo -u $BENCH_USER bench new-site $SITE_NAME \
    --admin-password "$(openssl rand -base64 12)" \
    --mariadb-root-password "$(sudo cat /etc/mysql/debian.cnf | grep password | head -1 | awk '{print $3}')"

# Install ERPNext
echo "Installing ERPNext..."
sudo -u $BENCH_USER bench get-app erpnext --branch version-15
sudo -u $BENCH_USER bench --site $SITE_NAME install-app erpnext

# Setup production
echo "Setting up production..."
sudo -u $BENCH_USER bench setup production $BENCH_USER

# Enable SSL
echo "Setting up SSL..."
sudo -u $BENCH_USER bench setup lets-encrypt $SITE_NAME

# Configure firewall
echo "Configuring firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Setup backups
echo "Configuring backups..."
sudo -u $BENCH_USER bench --site $SITE_NAME set-config backup_frequency "0 2 * * *"
sudo -u $BENCH_USER bench --site $SITE_NAME enable-scheduler

echo "=== Production setup complete ==="
echo "Site: $SITE_NAME"
echo "Admin password saved in: $BENCH_PATH/sites/$SITE_NAME/site_config.json"

# ─────────────────────────────────────────────────────────────────────────────
# bench update — risks and safe update procedure
# ─────────────────────────────────────────────────────────────────────────────
#
# `bench update` pulls the latest code for all apps, runs migrations, and
# restarts services.  Key risks:
#
#   1. Breaking schema migrations — always test on staging first.
#   2. Dependency conflicts — new app versions may require different Python
#      packages; check requirements.txt diffs before updating.
#   3. Custom patches may conflict with upstream patches.
#   4. Downtime — `bench update` restarts workers; schedule during low-traffic.
#
# Safe update workflow:
#   bench --site staging.local backup          # backup staging first
#   bench update --no-backup --reset           # test on staging
#   bench --site staging.local migrate
#   # Verify staging, then repeat on production:
#   bench --site $SITE_NAME backup
#   bench update
#
# ─────────────────────────────────────────────────────────────────────────────
# Database backup strategy
# ─────────────────────────────────────────────────────────────────────────────

backup_site() {
    local SITE="$1"
    local BACKUP_DIR="$BENCH_PATH/sites/backups"
    local TIMESTAMP=$(date +%Y%m%d_%H%M%S)

    echo "Creating backup for $SITE..."

    # Create compressed SQL + files backup
    sudo -u $BENCH_USER bench --site "$SITE" backup \
        --with-files \
        --compress

    echo "Backup created in $BACKUP_DIR"

    # Optional: push to S3 (requires awscli configured)
    # aws s3 sync "$BACKUP_DIR" "s3://your-bucket/frappe-backups/$SITE/" \
    #     --exclude "*" \
    #     --include "*.sql.gz" \
    #     --include "*.tar.gz"

    # Optional: push to GCS
    # gsutil -m rsync -r "$BACKUP_DIR" "gs://your-bucket/frappe-backups/$SITE/"
}

# Schedule daily backups via cron (add to frappe user's crontab):
# 0 2 * * * /home/frappe/frappe-bench/env/bin/bench --site <site> backup --with-files --compress

# ─────────────────────────────────────────────────────────────────────────────
# Rollback mechanism
# ─────────────────────────────────────────────────────────────────────────────

rollback_deployment() {
    local SITE="$1"
    local BACKUP_FILE="$2"   # path to .sql.gz backup file

    if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
        echo "ERROR: Provide a valid backup file path as the second argument."
        exit 1
    fi

    echo "=== Rolling back $SITE to $BACKUP_FILE ==="

    # 1. Enable maintenance mode to block incoming requests
    sudo -u $BENCH_USER bench --site "$SITE" set-maintenance-mode on

    # 2. Restore database from backup
    sudo -u $BENCH_USER bench --site "$SITE" restore "$BACKUP_FILE"

    # 3. Revert app code to the previous git tag/commit
    #    (assumes you tagged the release before updating)
    # cd $BENCH_PATH/apps/erpnext && git checkout <previous-tag>
    # cd $BENCH_PATH/apps/frappe  && git checkout <previous-tag>

    # 4. Rebuild assets for the restored version
    sudo -u $BENCH_USER bench build

    # 5. Restart services
    sudo supervisorctl restart all

    # 6. Disable maintenance mode
    sudo -u $BENCH_USER bench --site "$SITE" set-maintenance-mode off

    echo "=== Rollback complete for $SITE ==="
}

# Usage:
#   bash production_setup.sh <site-name>          # initial setup
#   source production_setup.sh && backup_site <site-name>
#   source production_setup.sh && rollback_deployment <site-name> /path/to/backup.sql.gz
