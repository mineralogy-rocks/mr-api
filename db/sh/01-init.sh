#!/bin/bash
set -e
export PGPASSWORD="$POSTGRES_PASSWORD";
pg_restore -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c ./backup/master_dump.sql
# psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@database:$POSTGRES_PORT/$POSTGRES_DB" -Fc < ./docker-entrypoint-initdb.d/master_dump.sql
# psql "postgresql://gpminerals:gpmineralsDB@database:5432/postgres" -Fc < ./docker-entrypoint-initdb.d/master_dump.sql