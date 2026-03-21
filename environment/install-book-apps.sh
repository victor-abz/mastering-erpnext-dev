#!/bin/bash
# ============================================================
# install-book-apps.sh
# Installs all three book project apps into a running
# frappe_docker bench container.
#
# Usage (run from your HOST machine, repo root):
#   bash environment/install-book-apps.sh [SITE_NAME] [CONTAINER]
#
# Defaults:
#   SITE_NAME  = frontend   (frappe_docker default)
#   CONTAINER  = backend    (frappe_docker backend service)
#
# Example:
#   bash environment/install-book-apps.sh
#   bash environment/install-book-apps.sh mysite.localhost backend
# ============================================================

set -e

SITE_NAME="${1:-frontend}"
CONTAINER="${2:-frappe_docker-backend-1}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Repo root  : $REPO_ROOT"
echo "==> Site name  : $SITE_NAME"
echo "==> Container  : $CONTAINER"
echo ""

# ── 1. Copy app source into the container ──────────────────
echo "==> Copying app source into container..."

for APP in asset_management_app production_planning_app vendor_portal_app; do
    case $APP in
        asset_management_app)   SRC="$REPO_ROOT/projects/asset_management/asset_management_app" ;;
        production_planning_app) SRC="$REPO_ROOT/projects/production_planning/production_planning_app" ;;
        vendor_portal_app)      SRC="$REPO_ROOT/projects/vendor_portal/vendor_portal_app" ;;
    esac

    echo "  Copying $APP..."
    docker cp "$SRC" "$CONTAINER:/home/frappe/frappe-bench/apps/$APP"
done

# ── 2. pip-install each app (editable) ─────────────────────
echo ""
echo "==> Installing apps into bench Python environment..."

for APP in asset_management_app production_planning_app vendor_portal_app; do
    echo "  pip install -e $APP"
    docker exec "$CONTAINER" bash -c \
        "cd /home/frappe/frappe-bench && ./env/bin/pip install -e apps/$APP -q"
done

# ── 3. Add apps to apps.txt ────────────────────────────────
echo ""
echo "==> Registering apps in bench..."

for APP in asset_management_app production_planning_app vendor_portal_app; do
    docker exec "$CONTAINER" bash -c \
        "grep -qxF '$APP' /home/frappe/frappe-bench/sites/apps.txt \
         || echo '$APP' >> /home/frappe/frappe-bench/sites/apps.txt"
done

# ── 4. Install apps on the site ────────────────────────────
echo ""
echo "==> Installing apps on site: $SITE_NAME"

for APP in asset_management_app production_planning_app vendor_portal_app; do
    echo "  bench --site $SITE_NAME install-app $APP"
    docker exec "$CONTAINER" bash -c \
        "cd /home/frappe/frappe-bench && bench --site $SITE_NAME install-app $APP"
done

# ── 5. Run migrations ──────────────────────────────────────
echo ""
echo "==> Running migrations..."
docker exec "$CONTAINER" bash -c \
    "cd /home/frappe/frappe-bench && bench --site $SITE_NAME migrate"

# ── 6. Clear cache ─────────────────────────────────────────
echo ""
echo "==> Clearing cache..."
docker exec "$CONTAINER" bash -c \
    "cd /home/frappe/frappe-bench && bench --site $SITE_NAME clear-cache"

echo ""
echo "✓ All three apps installed successfully on site: $SITE_NAME"
echo ""
echo "Next steps:"
echo "  Open ERPNext → http://localhost:8080  (or your frappe_docker port)"
echo "  Run tests:  bash environment/run-tests.sh $SITE_NAME $CONTAINER"
