start-db:
	@echo "--> Starting local database..."
	docker-compose up -d database

stop-db:
	@echo "--> Stopping local database..."
	docker-compose stop database

dump-prod-db:
	$(eval include ./.envs/.prod/.db)
	$(eval export $(shell sed 's/=.*//' ./.envs/.prod/.db))

	docker-compose -f docker-compose.yml run \
		-e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
		-e POSTGRES_HOST=${POSTGRES_HOST} \
		-e POSTGRES_PORT=${POSTGRES_PORT} \
		-e POSTGRES_USER=${POSTGRES_USER} \
		-e POSTGRES_DB=${POSTGRES_DB} --rm --no-deps database backup

backups:
	docker-compose -f docker-compose.yml run --rm database backups

restore-local-db:
	docker-compose -f docker-compose.yml run --rm --no-deps database restore "${backup}"

run-sql:
ifdef file
		$(eval include .dev.env)
		$(eval export $(shell sed 's/=.*//' .dev.env))

		@echo "--> Running sql..."

		docker-compose -f docker-compose.yml run --rm --no-deps database \
			psql "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:${POSTGRES_PORT}/${POSTGRES_DB}" -a -f file
else
		@echo 'please, pass sql file as an argument!'
endif

start:
	docker-compose -f docker-compose.yml up -d

stop:
	docker-compose -f docker-compose.yml down
