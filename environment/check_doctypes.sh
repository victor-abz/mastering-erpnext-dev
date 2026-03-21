#!/bin/bash
mysql -u root -padmin _855399d2650881d5 -e "SELECT name, module FROM tabDocType WHERE module IN ('Asset Management', 'Production Planning', 'Vendor Portal') ORDER BY module, name;"
