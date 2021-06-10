#!/usr/bin/bash
set -e

# Put your credentials below.
PGPASSWORD=$POSTGRES_PASSWORD_PROD;
docker-compose -f docker-compose.yml run --rm --no-deps database \
pg_dump --host=$POSTGRES_HOST_PROD --port=$POSTGRES_PORT_PROD dbname=$POSTGRES_DB_PROD --username=$POSTGRES_USER_PROD \
         --clean --no-owner --no-privileges > ./db/backup/db__$(date +%d.%m.%Y__%H-%M).sql