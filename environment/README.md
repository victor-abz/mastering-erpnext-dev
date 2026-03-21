# Environment Scripts

Scripts for setting up and testing the book's code against a running ERPNext instance.

## Prerequisites

- Docker with frappe_docker running (`docker ps` shows a `backend` container)
- The three project apps are in `projects/` (they are — this repo includes them)

## Scripts

| Script | Purpose |
|--------|---------|
| `install-book-apps.sh` | Copies + installs all 3 apps into your frappe_docker bench |
| `run-tests.sh` | Runs the full test suite (chapter 15) inside the container |
| `console.sh` | Opens an interactive bench console for manual testing |

## Quick Start

```bash
# Make scripts executable (Linux/macOS)
chmod +x environment/*.sh

# 1. Install apps (defaults: site=frontend, container=backend)
bash environment/install-book-apps.sh

# 2. Run tests
bash environment/run-tests.sh

# 3. Open console for interactive testing
bash environment/console.sh
```

## Custom site/container names

```bash
bash environment/install-book-apps.sh mysite.localhost backend
bash environment/run-tests.sh mysite.localhost backend asset_management_app
bash environment/console.sh mysite.localhost backend
```

## After editing code locally

```bash
# Sync changes into the container
docker cp projects/asset_management/asset_management_app/. \
    backend:/home/frappe/frappe-bench/apps/asset_management_app/

# Restart workers
docker exec backend bash -c "cd /home/frappe/frappe-bench && bench restart"
```
