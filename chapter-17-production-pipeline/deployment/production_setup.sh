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
