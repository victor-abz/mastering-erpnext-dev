#!/bin/bash

# Mastering ERPNext Development - Chapter 2
# Site Creation Script
# Creates new sites with different configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_DB_PASSWORD="root"
DEFAULT_ADMIN_PASSWORD="admin"

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

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] <site-name>"
    echo
    echo "Options:"
    echo "  -d, --db-password <password>    Database root password (default: root)"
    echo "  -a, --admin-password <password> Admin password (default: admin)"
    echo "  -e, --erpnext                  Install ERPNext (default)"
    echo "  -c, --custom <app-name>        Install custom app"
    echo "  -m, --mysql                    Use MySQL instead of MariaDB"
    echo "  -p, --postgres                 Use PostgreSQL instead of MariaDB"
    echo "  -s, --ssl                      Enable SSL"
    echo "  --dev-mode                     Enable developer mode"
    echo "  --demo-data                    Install demo data"
    echo "  --help                         Show this help message"
    echo
    echo "Examples:"
    echo "  $0 dev.local                   # Create development site with ERPNext"
    echo "  $0 --dev-mode test.local       # Create test site with dev mode"
    echo "  $0 --custom my_app prod.local  # Create production site with custom app"
}

# Parse command line arguments
parse_args() {
    SITE_NAME=""
    DB_PASSWORD="$DEFAULT_DB_PASSWORD"
    ADMIN_PASSWORD="$DEFAULT_ADMIN_PASSWORD"
    INSTALL_ERPNEXT=true
    CUSTOM_APPS=""
    DB_TYPE="mariadb"
    ENABLE_SSL=false
    DEV_MODE=false
    DEMO_DATA=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--db-password)
                DB_PASSWORD="$2"
                shift 2
                ;;
            -a|--admin-password)
                ADMIN_PASSWORD="$2"
                shift 2
                ;;
            -e|--erpnext)
                INSTALL_ERPNEXT=true
                shift
                ;;
            -c|--custom)
                CUSTOM_APPS="$2"
                shift 2
                ;;
            -m|--mysql)
                DB_TYPE="mysql"
                shift
                ;;
            -p|--postgres)
                DB_TYPE="postgres"
                shift
                ;;
            -s|--ssl)
                ENABLE_SSL=true
                shift
                ;;
            --dev-mode)
                DEV_MODE=true
                shift
                ;;
            --demo-data)
                DEMO_DATA=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            -*)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                if [ -z "$SITE_NAME" ]; then
                    SITE_NAME="$1"
                else
                    log_error "Multiple site names provided"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    if [ -z "$SITE_NAME" ]; then
        log_error "Site name is required"
        show_usage
        exit 1
    fi
    
    # Validate site name
    if [[ ! "$SITE_NAME" =~ ^[a-zA-Z0-9.-]+$ ]]; then
        log_error "Invalid site name. Use only letters, numbers, dots, and hyphens"
        exit 1
    fi
}

# Check if bench exists
check_bench() {
    if [ ! -f "bench" ]; then
        log_error "Not in a bench directory. Run this script from your bench root."
        exit 1
    fi
    
    if [ ! -f "apps/frappe/__init__.py" ]; then
        log_error "Frappe app not found. Make sure you're in a valid bench."
        exit 1
    fi
}

# Check if site already exists
check_site_exists() {
    if [ -d "sites/$SITE_NAME" ]; then
        log_warning "Site '$SITE_NAME' already exists"
        read -p "Do you want to remove it and recreate? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Removing existing site..."
            bench drop-site "$SITE_NAME" --force
        else
            log_info "Exiting..."
            exit 0
        fi
    fi
}

# Check database connection
check_database() {
    log_info "Checking database connection..."
    
    case "$DB_TYPE" in
        "mariadb"|"mysql")
            if ! mysql -u root -p"$DB_PASSWORD" -e "SELECT 1;" &>/dev/null; then
                log_error "Cannot connect to MySQL/MariaDB with root user"
                exit 1
            fi
            ;;
        "postgres")
            if ! psql -U postgres -c "SELECT 1;" &>/dev/null; then
                log_error "Cannot connect to PostgreSQL"
                exit 1
            fi
            ;;
    esac
    
    log_success "Database connection successful"
}

# Install required apps
install_apps() {
    log_info "Installing required apps..."
    
    if [ "$INSTALL_ERPNEXT" = true ]; then
        if [ ! -d "apps/erpnext" ]; then
            log_info "Installing ERPNext..."
            bench get-app https://github.com/frappe/erpnext --branch version-15
        fi
    fi
    
    if [ -n "$CUSTOM_APPS" ]; then
        IFS=',' read -ra APP_ARRAY <<< "$CUSTOM_APPS"
        for app in "${APP_ARRAY[@]}"; do
            app=$(echo "$app" | xargs)  # trim whitespace
            if [ ! -d "apps/$app" ]; then
                log_info "Installing custom app: $app"
                # Assume app is in local apps directory
                if [ -d "../$app" ]; then
                    bench get-app "../$app"
                else
                    log_error "Custom app '$app' not found"
                    exit 1
                fi
            fi
        done
    fi
    
    log_success "All required apps installed"
}

# Create the site
create_site() {
    log_info "Creating site: $SITE_NAME"
    
    # Build new-site command
    CMD="bench new-site $SITE_NAME"
    CMD="$CMD --mariadb-root-password $DB_PASSWORD"
    CMD="$CMD --admin-password $ADMIN_PASSWORD"
    
    if [ "$DB_TYPE" = "postgres" ]; then
        CMD="$CMD --db-type postgres"
    fi
    
    if [ "$ENABLE_SSL" = true ]; then
        CMD="$CMD --ssl-certificate /etc/ssl/certs/localhost.crt"
        CMD="$CMD --ssl-key /etc/ssl/private/localhost.key"
    fi
    
    # Execute command
    eval "$CMD"
    
    log_success "Site created successfully"
}

# Install apps on site
install_site_apps() {
    log_info "Installing apps on site..."
    
    if [ "$INSTALL_ERPNEXT" = true ]; then
        bench --site "$SITE_NAME" install-app erpnext
    fi
    
    if [ -n "$CUSTOM_APPS" ]; then
        IFS=',' read -ra APP_ARRAY <<< "$CUSTOM_APPS"
        for app in "${APP_ARRAY[@]}"; do
            app=$(echo "$app" | xargs)  # trim whitespace
            bench --site "$SITE_NAME" install-app "$app"
        done
    fi
    
    log_success "Apps installed on site"
}

# Configure site
configure_site() {
    log_info "Configuring site..."
    
    # Enable developer mode if requested
    if [ "$DEV_MODE" = true ]; then
        bench --site "$SITE_NAME" set-config developer_mode 1
        log_info "Developer mode enabled"
    fi
    
    # Install demo data if requested
    if [ "$DEMO_DATA" = true ]; then
        log_info "Installing demo data (this may take a while)..."
        bench --site "$SITE_NAME" install-demo
        log_success "Demo data installed"
    fi
    
    # Set as default site if it's the first site
    SITE_COUNT=$(bench get-sites | wc -l)
    if [ "$SITE_COUNT" -eq 1 ]; then
        bench use "$SITE_NAME"
        log_info "Set as default site"
    fi
    
    log_success "Site configuration completed"
}

# Create site-specific scripts
create_site_scripts() {
    log_info "Creating site-specific scripts..."
    
    # Create site start script
    cat > "start-$SITE_NAME.sh" << EOF
#!/bin/bash

# Start bench with $SITE_NAME as default site
cd "\$(dirname "\$0")"

bench use "$SITE_NAME"
bench start

echo "Bench is running at http://$SITE_NAME:8000"
echo "Login with: Administrator / $ADMIN_PASSWORD"
EOF
    
    chmod +x "start-$SITE_NAME.sh"
    
    # Create site backup script
    cat > "backup-$SITE_NAME.sh" << EOF
#!/bin/bash

# Backup $SITE_NAME
cd "\$(dirname "\$0")"

BACKUP_DIR="backups/\$(date +%Y%m%d_%H%M%S)"
mkdir -p "\$BACKUP_DIR"

bench --site "$SITE_NAME" backup --with-files --backup-path "\$BACKUP_DIR"

echo "Backup completed: \$BACKUP_DIR"
EOF
    
    chmod +x "backup-$SITE_NAME.sh"
    
    # Create site console script
    cat > "console-$SITE_NAME.sh" << EOF
#!/bin/bash

# Open console for $SITE_NAME
cd "\$(dirname "\$0")"

bench --site "$SITE_NAME" console
EOF
    
    chmod +x "console-$SITE_NAME.sh"
    
    log_success "Site scripts created"
}

# Show site information
show_site_info() {
    echo
    log_success "Site '$SITE_NAME' created successfully!"
    echo
    echo "Site Information:"
    echo "  URL:           http://$SITE_NAME:8000"
    echo "  Admin User:    Administrator"
    echo "  Admin Password: $ADMIN_PASSWORD"
    echo "  Database:      $DB_TYPE"
    echo "  Developer Mode: $DEV_MODE"
    echo
    echo "Useful Commands:"
    echo "  bench use $SITE_NAME                    # Set as default site"
    echo "  bench --site $SITE_NAME console         # Open Python console"
    echo "  bench --site $SITE_NAME migrate         # Run migrations"
    echo "  bench --site $SITE_NAME backup           # Backup site"
    echo "  bench --site $SITE_NAME restore <file>   # Restore from backup"
    echo
    echo "Site Scripts:"
    echo "  ./start-$SITE_NAME.sh                   # Start bench with this site"
    echo "  ./backup-$SITE_NAME.sh                  # Backup this site"
    echo "  ./console-$SITE_NAME.sh                 # Open console for this site"
    echo
}

# Main execution
main() {
    parse_args "$@"
    check_bench
    check_site_exists
    check_database
    install_apps
    create_site
    install_site_apps
    configure_site
    create_site_scripts
    show_site_info
}

# Run main function
main "$@"
