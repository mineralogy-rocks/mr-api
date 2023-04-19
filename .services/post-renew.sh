#!/usr/bin/env bash
set -e

cd /home/ubuntu/backend
/usr/bin/docker compose -f docker-compose.prod.yml exec -T nginx nginx -s reload
