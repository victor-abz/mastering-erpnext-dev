#!/bin/bash
# ============================================================
# console.sh
# Opens a bench console inside the frappe_docker container.
# This is the fastest way to test code interactively.
#
# Usage:
#   bash environment/console.sh [SITE_NAME] [CONTAINER]
#
# Defaults:
#   SITE_NAME  = frontend
#   CONTAINER  = backend
# ============================================================

SITE_NAME="${1:-frontend}"
CONTAINER="${2:-frappe_docker-backend-1}"

echo "Opening bench console on site: $SITE_NAME"
echo "Type 'exit' or Ctrl+D to quit."
echo ""

docker exec -it "$CONTAINER" bash -c \
    "cd /home/frappe/frappe-bench && bench --site $SITE_NAME console"
