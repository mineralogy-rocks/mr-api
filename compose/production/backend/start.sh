#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python manage.py migrate
python manage.py collectstatic --noinput

gunicorn wsgi:application --pythonpath 'src' --bind 0.0.0.0:8000 --worker-class=gevent --worker-connections=1000 --workers=3
