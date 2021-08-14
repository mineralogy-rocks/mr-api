#!/bin/sh
set -e

python manage.py collectstatic --no-input

exec "$@"
