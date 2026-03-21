#!/bin/bash
mysql -u root -padmin _855399d2650881d5 -e "SELECT app_name, app_version FROM \`tabInstalled Application\` ORDER BY idx;"
