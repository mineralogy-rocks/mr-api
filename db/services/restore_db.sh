#!/usr/bin/env bash
set -e

psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_PASSWORD:$POSTGRES_PORT/$POSTGRES_DB" -Fc < $@

