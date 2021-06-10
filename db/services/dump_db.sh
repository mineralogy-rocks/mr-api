#!/bin/bash
set -e

# Put your credentials below.

docker-compose -f ../../docker-compose.yml run --rm --no-deps database \
pg_dump "host=$POSTGRES_HOST_PROD port=$POSTGRES_PORT_PROD dbname=$POSTGRES_DB_PROD user=$POSTGRES_USER_PROD password=$POSTGRES_PASSWORD_PROD" \
         --clean --no-owner --no-privileges > ../backup/db__$(date +%d.%m.%Y__%H-%M).sql