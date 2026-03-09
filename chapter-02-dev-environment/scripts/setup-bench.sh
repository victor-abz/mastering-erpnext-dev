#!/bin/bash

# Mastering ERPNext Development - Chapter 2
# Professional Bench Setup Script
# Supports Ubuntu/Debian, macOS, and Windows WSL

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BENCH_NAME="frappe-bench"
FRAPPE_BRANCH="version-15"
ERPNEXT_BRANCH="version-15"
PYTHON_VERSION="3.10"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    
    log_info "Detected OS: $OS"
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check RAM
    if [[ "$OS" == "linux" ]] || [[ "$OS" == "macos" ]]; then
        RAM=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}' 2>/dev/null || \
              sysctl -n hw.memsize | awk '{printf "%.0f", $1/1024/1024/1024}' 2>/dev/null || echo "0")
        
        if [ "$RAM" -lt 4 ]; then
            log_warning "Less than 4GB RAM detected. Performance may be slow."
        else
            log_success "RAM: ${RAM}GB (OK)"
        fi
    fi
    
    # Check disk space
    DISK_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$DISK_SPACE" -lt 20 ]; then
        log_warning "Less than 20GB free disk space. You may run out of space."
    else
        log_success "Disk space: ${DISK_SPACE}GB available (OK)"
    fi
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."
    
    case "$OS" in
        "debian")
            sudo apt-get update
            sudo apt-get install -y \
                python3-dev python3-pip python3-venv \
                python3-setuptools python3-wheel \
                git redis-server \
                build-essential libssl-dev libffi-dev \
                libjpeg-dev libpng-dev libwebp-dev \
                xvfb libfontconfig1 libxrender1 \
                curl wget gnupg2 software-properties-common \
                mariadb-server mariadb-client \
                nodejs npm
            ;;
        "macos")
            # Check if Homebrew is installed
            if ! command -v brew &> /dev/null; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            brew update
            brew install python@3.10 git redis mariadb node
            ;;
        "redhat")
            sudo yum update -y
            sudo yum install -y \
                python3-devel python3-pip \
                git redis \
                gcc gcc-c++ openssl-devel libffi-devel \
                libjpeg-turbo-devel libpng-devel libwebp-devel \
                mariadb-server mariadb \
                nodejs npm
            ;;
        *)
            log_error "Unsupported OS: $OS"
            exit 1
            ;;
    esac
    
    log_success "System dependencies installed"
}

# Configure MariaDB
configure_mariadb() {
    log_info "Configuring MariaDB..."
    
    # Start MariaDB service
    case "$OS" in
        "debian"|"redhat")
            sudo systemctl start mariadb
            sudo systemctl enable mariadb
            ;;
        "macos")
            brew services start mariadb
            ;;
    esac
    
    # Secure installation (non-interactive)
    sudo mysql -e "
        DELETE FROM mysql.user WHERE User='';
        DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
        DROP DATABASE IF EXISTS test;
        DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
        FLUSH PRIVILEGES;
    "
    
    # Create Frappe database user
    sudo mysql -e "
        CREATE USER IF NOT EXISTS 'frappe'@'localhost' IDENTIFIED BY 'frappe';
        GRANT ALL PRIVILEGES ON *.* TO 'frappe'@'localhost';
        FLUSH PRIVILEGES;
    "
    
    log_success "MariaDB configured"
}

# Install Node.js dependencies
install_node_deps() {
    log_info "Installing Node.js dependencies..."
    
    # Install yarn globally
    sudo npm install -g yarn
    
    # Install frappe-cli
    sudo npm install -g frappe-cli
    
    log_success "Node.js dependencies installed"
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."
    
    # Create virtual environment
    python3 -m venv env
    source env/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install frappe-bench
    pip install frappe-bench
    
    log_success "Python dependencies installed"
}

# Create bench
create_bench() {
    log_info "Creating Frappe bench: $BENCH_NAME"
    
    # Check if bench already exists
    if [ -d "$BENCH_NAME" ]; then
        log_warning "Bench directory already exists. Removing it..."
        rm -rf "$BENCH_NAME"
    fi
    
    # Initialize bench
    bench init "$BENCH_NAME" \
        --frappe-path https://github.com/frappe/frappe \
        --frappe-branch "$FRAPPE_BRANCH" \
        --python "$(which python3)"
    
    cd "$BENCH_NAME"
    
    # Change to bench directory for subsequent commands
    log_success "Bench created successfully"
}

# Install ERPNext
install_erpnext() {
    log_info "Installing ERPNext..."
    
    # Get ERPNext
    bench get-app https://github.com/frappe/erpnext --branch "$ERPNEXT_BRANCH"
    
    log_success "ERPNext installed"
}

# Create new site
create_site() {
    log_info "Creating new site..."
    
    SITE_NAME="dev.local"
    
    # Create site
    bench new-site "$SITE_NAME" \
        --mariadb-root-password "root" \
        --admin-password "admin" \
        --install-app erpnext
    
    # Set as default site
    bench use "$SITE_NAME"
    
    log_success "Site created: $SITE_NAME"
    log_info "Access your site at: http://$SITE_NAME:8000"
    log_info "Login with: Administrator / admin"
}

# Setup development environment
setup_dev_env() {
    log_info "Setting up development environment..."
    
    # Enable developer mode
    bench --site dev.local set-config developer_mode 1
    
    # Install development dependencies
    bench setup requirements
    
    # Build assets
    bench build
    
    log_success "Development environment configured"
}

# Create startup script
create_startup_script() {
    log_info "Creating startup script..."
    
    cat > start-bench.sh << 'EOF'
#!/bin/bash

# Frappe Bench Startup Script

cd "$(dirname "$0")"

echo "Starting Frappe development server..."
bench start

echo "Bench is running at http://dev.local:8000"
echo "Press Ctrl+C to stop"
EOF
    
    chmod +x start-bench.sh
    
    log_success "Startup script created: start-bench.sh"
}

# Create utility scripts
create_utility_scripts() {
    log_info "Creating utility scripts..."
    
    # Backup script
    cat > backup-site.sh << 'EOF'
#!/bin/bash

# Backup all sites in bench
cd "$(dirname "$0")"

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

for site in $(bench get-sites); do
    echo "Backing up $site..."
    bench --site "$site" backup --with-files --backup-path "$BACKUP_DIR"
done

echo "Backup completed: $BACKUP_DIR"
EOF
    
    chmod +x backup-site.sh
    
    # Update script
    cat > update-bench.sh << 'EOF'
#!/bin/bash

# Update bench and all apps
cd "$(dirname "$0")"

echo "Updating bench..."
bench update

echo "Running migrations..."
bench migrate

echo "Rebuilding assets..."
bench build

echo "Update completed!"
EOF
    
    chmod +x update-bench.sh
    
    log_success "Utility scripts created"
}

# Print next steps
print_next_steps() {
    echo
    log_success "Bench setup completed successfully!"
    echo
    echo "Next steps:"
    echo "1. cd $BENCH_NAME"
    echo "2. ./start-bench.sh"
    echo "3. Open http://dev.local:8000 in your browser"
    echo "4. Login with Administrator / admin"
    echo
    echo "Useful commands:"
    echo "- bench console                 # Python console"
    echo "- bench --site dev.local console  # Site-specific console"
    echo "- bench doctor                 # Check system health"
    echo "- bench restart                # Restart services"
    echo
    echo "For development:"
    echo "- bench new-app my_app         # Create new app"
    echo "- bench --site dev.local install-app my_app  # Install app"
    echo
}

# Main execution
main() {
    log_info "Starting Frappe Bench setup..."
    
    detect_os
    check_requirements
    
    if [ "$OS" == "unknown" ]; then
        log_error "Unsupported operating system"
        exit 1
    fi
    
    install_system_deps
    configure_mariadb
    install_node_deps
    install_python_deps
    create_bench
    install_erpnext
    create_site
    setup_dev_env
    create_startup_script
    create_utility_scripts
    print_next_steps
    
    log_success "Setup completed successfully!"
}

# Run main function
main "$@"
