#!/usr/bin/env bash
set -e

cd /home/ubuntu/backend
/usr/bin/docker compose -f docker-compose.prod.yaml exec -T nginx nginx -s reload
