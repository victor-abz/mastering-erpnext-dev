#!/bin/bash
mysql -u root -padmin _855399d2650881d5 -e "SELECT name, module FROM tabWorkspace WHERE module IN ('Asset Management', 'Production Planning', 'Vendor Portal');"
