#!/usr/bin/env bash
export $(grep -v '^#' ./.dev.env | xargs -d '\n')

set -e

pg_restore -h 127.0.0.1 -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -Fc -c ./db/backup/master_dump.sql

# psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@127.0.0.1:$POSTGRES_PORT/$POSTGRES_DB" -Fc < ./db/backup/master_dump.sql