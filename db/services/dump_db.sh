#!/usr/bin/bash
export $(grep -v '^#' ./.prod.env | xargs -d '\n')
set -e

# Put your credentials below.
PGPASSWORD=$POSTGRES_PASSWORD;
PGDATABASE=$POSTGRES_DB;

echo "$POSTGRES_DB";

docker-compose -f docker-compose.yml run --rm --no-deps database \
pg_dump "host=$POSTGRES_HOST port=$POSTGRES_PORT dbname=$POSTGRES_DB user=$POSTGRES_USER password=$POSTGRES_PASSWORD" \
--clean --no-owner --no-privileges > ./db/backup/db__$(date +%d.%m.%Y__%H-%M).sql

# pg_dump --host=$POSTGRES_HOST --port=$POSTGRES_PORT --username=$POSTGRES_USER \
#          --clean --no-password --no-owner --no-privileges > ./db/backup/db__$(date +%d.%m.%Y__%H-%M).sql


# unset $(grep -v '^#' ./.prod.env | sed -E 's/(.*)=.*/\1/' | xargs)