#!/usr/bin/env bash
export $(grep -v '^#' ./.dev.env | xargs -d '\n')

set -e

psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@127.0.0.1:$POSTGRES_PORT/$POSTGRES_DB" -Fc < ./db/backup/master_dump.sql