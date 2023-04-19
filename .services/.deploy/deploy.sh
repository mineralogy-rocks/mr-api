#!/usr/bin/env bash
set -e

export COMPOSE_INTERACTIVE_NO_CLI=1

echo 'Changing directory to project repository...'
cd ./backend

echo 'Setting cronjobs...'
sudo cp ./.services/crontab/config /etc/cron.d/backend

echo 'Setting environment variables...'
source ./.envs/.prod/.do

echo 'Pulling latest source code...'
git pull

# echo 'Building latest nginx image...'
# docker compose -f docker-compose.prod.yaml build nginx

# echo 'Logging into DigitalOcean container registry...'
# doctl registry login --expiry-seconds 300

# echo 'Pulling latest backend image...'
# docker pull registry.digitalocean.com/mr-project/backend:latest

# echo 'Restarting containers...'
# docker compose -f docker-compose.prod.yaml up -d --no-deps backend nginx

export COMPOSE_INTERACTIVE_NO_CLI=0
