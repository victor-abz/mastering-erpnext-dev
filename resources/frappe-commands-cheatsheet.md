# Frappe Commands Cheatsheet

## Bench Commands

### Initialization & Setup

```bash
# Initialize a new bench
bench init <bench-name>

# Initialize with specific Frappe branch
bench init <bench-name> --frappe-branch version-15

# Initialize with specific Python version
bench init <bench-name> --python python3.10

# Create new app
bench new-app <app-name>

# Create new site
bench new-site <site-name>

# Create site with admin password
bench new-site <site-name> --admin-password <password>

# Create site with MySQL
bench new-site <site-name> --db-type mysql

# Install app on all sites
bench install-app <app-name>

# Install app on specific site
bench --site <site-name> install-app <app-name>

# Remove app
bench remove-app <app-name>

# Update app
bench update-app <app-name>

# Switch to specific branch
bench switch-to-branch <branch> <app-name>
```

### Site Management

```bash
# Switch active site
bench use <site-name>

# Get all sites
bench get-sites

# Migrate all sites
bench migrate

# Migrate specific site
bench --site <site-name> migrate

# Backup all sites
bench backup

# Backup specific site
bench --site <site-name> backup

# Backup with files
bench --site <site-name> backup --with-files

# Restore site
bench --site <site-name> restore <backup-file>

# Reinstall site
bench --site <site-name> reinstall

# Drop site
bench drop-site <site-name>

# Drop site with force
bench drop-site <site-name> --force
```

### Development Commands

```bash
# Start development server
bench start

# Restart services
bench restart

# Stop services
bench stop

# Check system health
bench doctor

# Watch for file changes
bench --site <site-name> watch

# Build assets
bench build

# Build assets for production
bench build --production

# Clear cache
bench clear-cache

# Clear site cache
bench --site <site-name> clear-cache

# Clear all caches
bench clear-all-cache

# Execute Python console
bench console

# Execute site-specific console
bench --site <site-name> console

# Execute shell command
bench --site <site-name> execute <command>

# Run server script
bench --site <site-name> run-script <script-file>

# Run tests
bench --site <site-name> test

# Run specific test
bench --site <site-name> test <test-name>

# Run tests with coverage
bench --site <site-name> test --coverage
```

### Configuration

```bash
# Get configuration
bench config

# Set configuration
bench config <key> <value>

# Set multiple configurations
bench config --set <key>=<value>

# Get site configuration
bench --site <site-name> get-config

# Set site configuration
bench --site <site-name> set-config <key> <value>

# Enable developer mode
bench --site <site-name> set-config developer_mode 1

# Disable developer mode
bench --site <site-name> set-config developer_mode 0

# Enable maintenance mode
bench --site <site-name> set-config maintenance_mode 1

# Disable maintenance mode
bench --site <site-name> set-config maintenance_mode 0
```

### Updates & Maintenance

```bash
# Update all apps
bench update

# Update specific app
bench update-app <app-name>

# Update with patches
bench update --patch

# Update with restart
bench update --restart

# Update with build
bench update --build

# Migrate after update
bench update --migrate

# Update requirements
bench setup requirements

# Update pip packages
bench setup pip

# Update node packages
bench setup node

# Rebuild search index
bench --site <site-name> rebuild-search

# Rebuild permissions
bench --site <site-name> rebuild-permissions

# Reset permissions
bench --site <site-name> reset-permissions
```

## Database Commands

### Database Operations

```bash
# Connect to database
bench --site <site-name> mariadb

# Connect to MariaDB with credentials
bench --site <site-name> mariadb --host <host> --port <port>

# Execute SQL query
bench --site <site-name> execute "SELECT * FROM tabUser"

# Execute SQL file
bench --site <site-name> execute-file <sql-file>

# Export database
bench --site <site-name> export-db

# Import database
bench --site <site-name> import-db <sql-file>

# Create database backup
bench --site <site-name> db-backup

# Restore database backup
bench --site <site-name> db-restore <backup-file>
```

## App Development Commands

### App Management

```bash
# Get app
bench get-app <app-url>

# Get app with branch
bench get-app <app-url> --branch <branch-name>

# Get app from local directory
bench get-app <local-path>

# Create new app
bench new-app <app-name>

# Create app with standard structure
bench new-app <app-name> --standard

# Create app with specific module
bench new-app <app-name> --module <module-name>

# Install app
bench install-app <app-name>

# Uninstall app
bench uninstall-app <app-name>

# Remove app
bench remove-app <app-name>

# Update app
bench update-app <app-name>

# Switch app branch
bench switch-to-branch <branch> <app-name>

# Get app status
bench --site <site-name> app-status <app-name>
```

### DocType Management

```bash
# Create new DocType
bench --site <site-name> create-doctype <doctype-name>

# Create DocType in module
bench --site <site-name> create-doctype <doctype-name> --module <module-name>

# Create custom DocType
bench --site <site-name> create-custom-doctype <doctype-name>

# Export DocType
bench --site <site-name> export-doc <doctype-name>

# Import DocType
bench --site <site-name> import-doc <json-file>

# Delete DocType
bench --site <site-name> delete-doctype <doctype-name>

# Reset DocType
bench --site <site-name> reset-doctype <doctype-name>
```

## Utility Commands

### File Operations

```bash
# Copy files from app to site
bench --site <site-name> copy-app-files <app-name>

# Migrate files
bench --site <site-name> migrate-files

# Restore files
bench --site <site-name> restore-files

# Sync files
bench --site <site-name> sync-files

# Check file integrity
bench --site <site-name> check-files
```

### User Management

```bash
# Create user
bench --site <site-name> create-user <email> --first-name <name> --password <password>

# Add user to role
bench --site <site-name> add-user-to-role <email> <role>

# Remove user from role
bench --site <site-name> remove-user-from-role <email> <role>

# Reset user password
bench --site <site-name> reset-password <email> <new-password>

# Enable user
bench --site <site-name> enable-user <email>

# Disable user
bench --site <site-name> disable-user <email>

# Get user list
bench --site <site-name> get-user-list
```

### Language & Localization

```bash
# Install language
bench --site <site-name> install-language <language-code>

# Uninstall language
bench --site <site-name> uninstall-language <language-code>

# Update language
bench --site <site-name> update-language <language-code>

# Get translation files
bench --site <site-name> get-translation-files <language-code>

# Build translation files
bench --site <site-name> build-translation-files <language-code>

# Import translations
bench --site <site-name> import-translations <csv-file>

# Export translations
bench --site <site-name> export-translations <language-code>
```

## Performance Commands

### Performance Optimization

```bash
# Optimize database
bench --site <site-name> optimize-db

# Analyze tables
bench --site <site-name> analyze-tables

# Repair database
bench --site <site-name> repair-db

# Clear cache
bench clear-cache

# Clear Redis cache
bench --site <site-name> clear-redis-cache

# Rebuild search index
bench --site <site-name> rebuild-search

# Update schema
bench --site <site-name> update-schema

# Check database integrity
bench --site <site-name> check-integrity
```

## Monitoring & Debugging

### Logging & Debugging

```bash
# Show logs
bench logs

# Show specific log
bench logs --log <log-name>

# Show logs with tail
bench logs --tail

# Show logs for specific site
bench --site <site-name> logs

# Enable debug mode
bench --site <site-name> set-config debug 1

# Disable debug mode
bench --site <site-name> set-config debug 0

# Show worker status
bench show-worker-status

# Restart workers
bench restart-workers

# Kill workers
bench kill-workers

# Show process list
bench --site <site-name> process-list
```

## Deployment Commands

### Production Setup

```bash
# Setup production
bench setup production

# Setup production with user
bench setup production --user <username>

# Setup supervisor
bench setup supervisor

# Setup nginx
bench setup nginx

# Setup SSL
bench setup ssl <site-name>

# Setup backup
bench setup backup

# Setup auto-update
bench setup auto-update

# Setup cron jobs
bench setup cron

# Remove cron jobs
bench remove-cron
```

## Advanced Commands

### Advanced Operations

```bash
# Execute custom script
bench --site <site-name> execute <python-code>

# Run server script
bench --site <site-name> run-server-script <script>

# Execute API method
bench --site <site-name> execute-api <method>

# Generate API key
bench --site <site-name> generate-api-key <user>

# Revoke API key
bench --site <site-name> revoke-api-key <api-key>

# Get API secrets
bench --site <site-name> get-api-secrets <user>

# Set API secrets
bench --site <site-name> set-api-secrets <user> <secrets>

# Export fixtures
bench --site <site-name> export-fixtures

# Import fixtures
bench --site <site-name> import-fixtures <fixture-file>

# Create patch
bench create-patch <patch-name>

# Apply patch
bench --site <site-name> apply-patch <patch-name>

# Update patches
bench update-patches
```

## Quick Reference

### Common Workflows

```bash
# New app development workflow
bench new-app my_app
bench new-app my_app --standard
bench --site dev.local install-app my_app
bench --site dev.local create-doctype MyDocType --module my_app

# Site setup workflow
bench new-site mysite.local
bench use mysite.local
bench --site mysite.local install-app erpnext
bench --site mysite.local set-config developer_mode 1
bench start

# Update workflow
bench update
bench migrate
bench build
bench restart

# Backup workflow
bench --site mysite.local backup --with-files
bench --site mysite.local restore backup-file.sql
```

### Troubleshooting

```bash
# Check system health
bench doctor

# Check worker status
bench show-worker-status

# Clear all caches
bench clear-all-cache

# Restart services
bench restart

# Check logs
bench logs --tail

# Rebuild permissions
bench --site mysite.local rebuild-permissions

# Reset database
bench --site mysite.local reinstall
```

---

## Tips & Tricks

1. **Always use `bench doctor`** when troubleshooting issues
2. **Clear cache** before reporting bugs
3. **Use developer mode** during development
4. **Backup regularly** before major changes
5. **Check logs** for error details
6. **Use specific site commands** when working with multiple sites
7. **Update requirements** after pulling changes
8. **Build assets** after CSS/JS changes
9. **Test in development** before production deployment
10. **Monitor worker processes** for performance issues
