#!/bin/bash

# Mastering ERPNext Development - Chapter 2
# App Installation Script
# Installs and configures Frappe apps

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo "Usage: $0 [OPTIONS] <app-source>"
    echo
    echo "App Sources:"
    echo "  github:<username>/<repo>[:<branch>]    Install from GitHub"
    echo "  local:<path>                           Install from local directory"
    echo "  url:<git-url>[:<branch>]              Install from any Git repository"
    echo "  erpnext                               Install ERPNext"
    echo
    echo "Options:"
    echo "  -s, --site <site-name>                Install on specific site (default: all sites)"
    echo "  -b, --branch <branch>                 Specify branch (overrides source branch)"
    echo "  -f, --force                           Force reinstall if app exists"
    echo "  -d, --dev                             Install in development mode"
    echo "  -r, --requirements                    Install requirements only"
    echo "  --skip-migrate                        Skip database migrations"
    echo "  --skip-build                          Skip building assets"
    echo "  --help                                Show this help message"
    echo
    echo "Examples:"
    echo "  $0 erpnext                           # Install ERPNext"
    echo "  $0 github:frappe/erpnext:version-15  # Install ERPNext v15 from GitHub"
    echo "  $0 local:../my_app                   # Install from local directory"
    echo "  $0 --site dev.local github:user/app  # Install on specific site"
}

# Parse command line arguments
parse_args() {
    APP_SOURCE=""
    SITE_NAME=""
    BRANCH=""
    FORCE=false
    DEV_MODE=false
    REQUIREMENTS_ONLY=false
    SKIP_MIGRATE=false
    SKIP_BUILD=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--site)
                SITE_NAME="$2"
                shift 2
                ;;
            -b|--branch)
                BRANCH="$2"
                shift 2
                ;;
            -f|--force)
                FORCE=true
                shift
                ;;
            -d|--dev)
                DEV_MODE=true
                shift
                ;;
            -r|--requirements)
                REQUIREMENTS_ONLY=true
                shift
                ;;
            --skip-migrate)
                SKIP_MIGRATE=true
                shift
                ;;
            --skip-build)
                SKIP_BUILD=true
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
                if [ -z "$APP_SOURCE" ]; then
                    APP_SOURCE="$1"
                else
                    log_error "Multiple app sources provided"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    if [ -z "$APP_SOURCE" ]; then
        log_error "App source is required"
        show_usage
        exit 1
    fi
}

# Check if bench exists
check_bench() {
    if [ ! -f "bench" ]; then
        log_error "Not in a bench directory. Run this script from your bench root."
        exit 1
    fi
}

# Parse app source
parse_app_source() {
    if [[ "$APP_SOURCE" == "github:"* ]]; then
        SOURCE_TYPE="github"
        REPO_INFO="${APP_SOURCE#github:}"
        
        if [[ "$REPO_INFO" == *":"* ]]; then
            GITHUB_REPO="${REPO_INFO%:*}"
            SOURCE_BRANCH="${REPO_INFO#*:}"
        else
            GITHUB_REPO="$REPO_INFO"
            SOURCE_BRANCH=""
        fi
        
        APP_URL="https://github.com/$GITHUB_REPO"
        APP_NAME=$(basename "$GITHUB_REPO")
        
    elif [[ "$APP_SOURCE" == "local:"* ]]; then
        SOURCE_TYPE="local"
        LOCAL_PATH="${APP_SOURCE#local:}"
        
        if [ ! -d "$LOCAL_PATH" ]; then
            log_error "Local app directory not found: $LOCAL_PATH"
            exit 1
        fi
        
        APP_URL="$LOCAL_PATH"
        APP_NAME=$(basename "$LOCAL_PATH")
        
    elif [[ "$APP_SOURCE" == "url:"* ]]; then
        SOURCE_TYPE="url"
        GIT_URL="${APP_SOURCE#url:}"
        
        if [[ "$GIT_URL" == *":"* ]]; then
            APP_URL="${GIT_URL%:*}"
            SOURCE_BRANCH="${GIT_URL#*:}"
        else
            APP_URL="$GIT_URL"
            SOURCE_BRANCH=""
        fi
        
        APP_NAME=$(basename "$APP_URL" .git)
        
    elif [ "$APP_SOURCE" = "erpnext" ]; then
        SOURCE_TYPE="github"
        APP_URL="https://github.com/frappe/erpnext"
        APP_NAME="erpnext"
        SOURCE_BRANCH="version-15"
        
    else
        log_error "Invalid app source format"
        show_usage
        exit 1
    fi
    
    # Override branch if specified
    if [ -n "$BRANCH" ]; then
        SOURCE_BRANCH="$BRANCH"
    fi
    
    log_info "Parsed app source:"
    log_info "  Type: $SOURCE_TYPE"
    log_info "  URL: $APP_URL"
    log_info "  Name: $APP_NAME"
    log_info "  Branch: ${SOURCE_BRANCH:-default}"
}

# Check if app already exists
check_app_exists() {
    if [ -d "apps/$APP_NAME" ]; then
        if [ "$FORCE" = true ]; then
            log_warning "App '$APP_NAME' already exists. Removing..."
            bench remove-app "$APP_NAME" --force
        else
            log_error "App '$APP_NAME' already exists. Use --force to reinstall."
            exit 1
        fi
    fi
}

# Get app
get_app() {
    log_info "Getting app: $APP_NAME"
    
    CMD="bench get-app"
    
    case "$SOURCE_TYPE" in
        "github"|"url")
            CMD="$CMD $APP_URL"
            if [ -n "$SOURCE_BRANCH" ]; then
                CMD="$CMD --branch $SOURCE_BRANCH"
            fi
            ;;
        "local")
            CMD="$CMD $APP_URL"
            ;;
    esac
    
    if [ "$DEV_MODE" = true ]; then
        CMD="$CMD --develop"
    fi
    
    eval "$CMD"
    
    log_success "App '$APP_NAME' downloaded"
}

# Install requirements
install_requirements() {
    log_info "Installing app requirements..."
    
    if [ -f "apps/$APP_NAME/requirements.txt" ]; then
        log_info "Installing Python requirements..."
        source env/bin/activate
        pip install -r "apps/$APP_NAME/requirements.txt"
    fi
    
    if [ -f "apps/$APP_NAME/package.json" ]; then
        log_info "Installing Node.js requirements..."
        cd "apps/$APP_NAME"
        npm install
        cd ../..
    fi
    
    if [ -f "apps/$APP_NAME/yarn.lock" ]; then
        log_info "Installing Node.js requirements with yarn..."
        cd "apps/$APP_NAME"
        yarn install
        cd ../..
    fi
    
    log_success "Requirements installed"
}

# Get target sites
get_target_sites() {
    if [ -n "$SITE_NAME" ]; then
        if [ ! -d "sites/$SITE_NAME" ]; then
            log_error "Site '$SITE_NAME' not found"
            exit 1
        fi
        SITES=("$SITE_NAME")
    else
        mapfile -t SITES < <(bench get-sites)
    fi
    
    log_info "Target sites: ${SITES[*]}"
}

# Install app on sites
install_on_sites() {
    for site in "${SITES[@]}"; do
        log_info "Installing app on site: $site"
        
        bench --site "$site" install-app "$APP_NAME"
        
        log_success "App installed on $site"
    done
}

# Run migrations
run_migrations() {
    if [ "$SKIP_MIGRATE" = false ]; then
        for site in "${SITES[@]}"; do
            log_info "Running migrations on site: $site"
            bench --site "$site" migrate
        done
        log_success "Migrations completed"
    else
        log_info "Skipping migrations"
    fi
}

# Build assets
build_assets() {
    if [ "$SKIP_BUILD" = false ]; then
        log_info "Building assets..."
        bench build
        log_success "Assets built"
    else
        log_info "Skipping asset build"
    fi
}

# Create app management scripts
create_app_scripts() {
    log_info "Creating app management scripts..."
    
    # Create app update script
    cat > "update-$APP_NAME.sh" << EOF
#!/bin/bash

# Update $APP_NAME app
cd "\$(dirname "\$0")"

echo "Updating $APP_NAME..."
bench update-app $APP_NAME

echo "Running migrations..."
bench migrate

echo "Building assets..."
bench build

echo "$APP_NAME updated successfully!"
EOF
    
    chmod +x "update-$APP_NAME.sh"
    
    # Create app remove script
    cat > "remove-$APP_NAME.sh" << EOF
#!/bin/bash

# Remove $APP_NAME app
cd "\$(dirname "\$0")"

read -p "Are you sure you want to remove $APP_NAME? (y/N): " -n 1 -r
echo
if [[ \$REPLY =~ ^[Yy]\$ ]]; then
    echo "Removing $APP_NAME..."
    bench remove-app $APP_NAME
    echo "$APP_NAME removed successfully!"
else
    echo "Operation cancelled."
fi
EOF
    
    chmod +x "remove-$APP_NAME.sh"
    
    log_success "App management scripts created"
}

# Show app information
show_app_info() {
    echo
    log_success "App '$APP_NAME' installed successfully!"
    echo
    echo "App Information:"
    echo "  Name: $APP_NAME"
    echo "  Source: $APP_URL"
    echo "  Branch: ${SOURCE_BRANCH:-default}"
    echo "  Installed on: ${SITES[*]}"
    echo
    echo "Useful Commands:"
    echo "  bench --site <site> install-app $APP_NAME    # Install on additional site"
    echo "  bench --site <site> uninstall-app $APP_NAME   # Uninstall from site"
    echo "  bench remove-app $APP_NAME                    # Remove from bench"
    echo "  bench update-app $APP_NAME                    # Update app"
    echo
    echo "App Scripts:"
    echo "  ./update-$APP_NAME.sh                         # Update app"
    echo "  ./remove-$APP_NAME.sh                         # Remove app"
    echo
}

# Main execution
main() {
    parse_args "$@"
    check_bench
    parse_app_source
    check_app_exists
    get_app
    
    if [ "$REQUIREMENTS_ONLY" = false ]; then
        get_target_sites
        install_on_sites
        run_migrations
        build_assets
    fi
    
    install_requirements
    create_app_scripts
    show_app_info
}

# Run main function
main "$@"
