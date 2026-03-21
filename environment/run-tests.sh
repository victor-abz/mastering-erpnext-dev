#!/bin/bash
# ============================================================
# run-tests.sh
# Runs the book's test suite inside the frappe_docker container.
#
# Usage:
#   bash environment/run-tests.sh [SITE_NAME] [CONTAINER] [APP]
#
# Defaults:
#   SITE_NAME  = frontend
#   CONTAINER  = backend
#   APP        = (all three apps)
#
# Examples:
#   bash environment/run-tests.sh
#   bash environment/run-tests.sh frontend backend asset_management_app
# ============================================================

set -e

SITE_NAME="${1:-frontend}"
CONTAINER="${2:-frappe_docker-backend-1}"
APP_FILTER="${3:-}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Site: $SITE_NAME  |  Container: $CONTAINER"
echo ""

# Copy latest test files into the container before running
echo "==> Syncing test files..."
for APP in asset_management_app production_planning_app vendor_portal_app; do
    case $APP in
        asset_management_app)   SRC="$REPO_ROOT/projects/asset_management/asset_management_app" ;;
        production_planning_app) SRC="$REPO_ROOT/projects/production_planning/production_planning_app" ;;
        vendor_portal_app)      SRC="$REPO_ROOT/projects/vendor_portal/vendor_portal_app" ;;
    esac
    docker cp "$SRC/." "$CONTAINER:/home/frappe/frappe-bench/apps/$APP/"
done

# Also sync the chapter-15 standalone tests
docker cp "$REPO_ROOT/chapter-15-automated-testing/tests/." \
    "$CONTAINER:/home/frappe/frappe-bench/apps/asset_management_app/asset_management/tests/"

echo ""

if [ -n "$APP_FILTER" ]; then
    echo "==> Running tests for: $APP_FILTER"
    docker exec "$CONTAINER" bash -c \
        "cd /home/frappe/frappe-bench && \
         bench --site $SITE_NAME run-tests --app $APP_FILTER --verbose"
else
    echo "==> Running tests for all book apps..."
    for APP in asset_management_app production_planning_app vendor_portal_app; do
        echo ""
        echo "── $APP ──────────────────────────────────────"
        docker exec "$CONTAINER" bash -c \
            "cd /home/frappe/frappe-bench && \
             bench --site $SITE_NAME run-tests --app $APP --verbose" || true
    done
fi

echo ""
echo "✓ Test run complete."
