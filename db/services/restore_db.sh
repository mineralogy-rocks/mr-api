#!/usr/bin/env bash
export $(grep -v '^#' ./.dev.env | xargs -d '\n')

set -e

docker-compose -f docker-compose.yml run --rm --no-deps database \
    psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@database:$POSTGRES_PORT/$POSTGRES_DB" -Fc < ./db/backup/master_dump.sql
