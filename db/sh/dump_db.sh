#!/bin/bash
set -e

# Put your credentials below.

docker-compose -f ../../docker-compose.yml run --rm --no-deps db \
mysqldump --host=gta-dev.cp7esvs8xwum.eu-west-1.rds.amazonaws.com \
		  --user=gta_prod_master \
		  --password='[m&pa:Wp#%9FAfHe' \
		  > ../_data/db/backup/db__$(date +%d.%m.%Y__%H-%M).sql