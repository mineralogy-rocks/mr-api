#!/bin/bash
set -e
export PGPASSWORD=$DATABASE_PASSWORD;
pg_restore -h 127.0.0.1 -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME -c ./db/master_dump.sql