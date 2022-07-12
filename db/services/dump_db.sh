#!/usr/bin/bash
export $(grep -v '^#' ./.prod.env | xargs -d '\n')
set -e

docker-compose -f docker-compose.yml run --rm --no-deps database \
    pg_dump "host=$POSTGRES_HOST port=$POSTGRES_PORT dbname=$POSTGRES_DB user=$POSTGRES_USER password=$POSTGRES_PASSWORD" \
    --clean --no-owner --no-privileges > ./db/backup/master_dump.sql

# unset $(grep -v '^#' ./.prod.env | sed -E 's/(.*)=.*/\1/' | xargs)
