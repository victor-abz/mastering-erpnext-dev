# ============================================================
# fix-after-restart.ps1
# Run this after restarting the frappe_docker containers.
# The .pth file that makes book apps importable is lost on
# container restart — this script restores it.
#
# Usage:
#   .\environment\fix-after-restart.ps1
# ============================================================

param(
    [string]$Container = "frappe_docker-backend-1"
)

Write-Host "==> Restoring Python path for book apps..."
docker exec $Container bash -c "echo '/home/frappe/frappe-bench/apps' > /home/frappe/frappe-bench/env/lib/python3.14/site-packages/frappe_apps.pth"

Write-Host "==> Restarting backend container..."
docker restart $Container

Write-Host ""
Write-Host "Waiting for gunicorn to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

$logs = docker logs $Container --tail 5 2>&1
Write-Host $logs

Write-Host ""
Write-Host "Done. Open http://localhost:8080/app" -ForegroundColor Green
