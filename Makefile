start-db:
	@echo "--> Starting local database..."
	docker-compose up -d database

stop-db:
	@echo "--> Stopping local database..."
	docker-compose stop database

dump-prod-db:
	$(eval include .prod.env)
	$(eval export $(shell sed 's/=.*//' .prod.env))

	@echo "--> Dumping prod database..."

	docker-compose -f docker-compose.yml run -e PGPASSWORD=${POSTGRES_PASSWORD} --rm --no-deps database \
		pg_dump --host=${POSTGRES_HOST} \
				--port=${POSTGRES_PORT} \
				--dbname=${POSTGRES_DB} \
				--user=${POSTGRES_USER} \
				--clean --no-owner --no-privileges > ./db/backup/master_dump.sql

restore-local-db:
	$(eval include .dev.env)
	$(eval export $(shell sed 's/=.*//' .dev.env))

	@echo "--> Restorign local database..."

	docker-compose -f docker-compose.yml run --rm --no-deps database \
		psql "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:${POSTGRES_PORT}/${POSTGRES_DB}" -Fc < ./db/backup/master_dump.sql

start:
	docker-compose up -d

stop:
	docker-compose down