.PHONY: build start stop restart sh tsh logs config lint db tdb mstart mstop clear migrate tmigrate rollback trollback

# \
!ifdef USE_LEGACY_DOCKER # \
compose_config=-f docker-compose.yml -f docker-compose-legacy.yml # \
!else
compose_config=-f docker-compose.yml
# \
!endif

# \
!ifndef 0 # \
test_env="DB_URL=$$TEST_DB_URL" # \
!else
test_env=DB_URL=\$$TEST_DB_URL
# \
!endif

container=mycalendar

# build the mycalendar container
build:
	docker-compose $(compose_config) build

# start all the containers
start:
	docker-compose $(compose_config) up -d

# stop all the containers
stop:
	docker-compose $(compose_config) down

# restart the mycalendar container
restart: stop start

# get a shell within the app container
sh:
	docker-compose $(compose_config) exec $(container) /bin/sh

tsh:
	docker-compose $(compose_config) exec $(container) /bin/sh -c "$(test_env) sh"

# run tests
test:
	docker-compose $(compose_config) exec $(container) /bin/sh -c "$(test_env) poetry run nose2 -v"

# check console output
logs:
	docker-compose $(compose_config) logs -f

# show the combined compose file used
config:
	docker-compose $(compose_config) config

# lint code
lint:
	docker-compose $(compose_config) exec $(container) poetry run autoflake --remove-all-unused-imports --ignore-init-module-imports --in-place --recursive mycalendar tests alembic
	docker-compose $(compose_config) exec $(container) poetry run isort mycalendar tests alembic
	docker-compose $(compose_config) exec $(container) poetry run black mycalendar tests alembic

db:
	docker-compose $(compose_config) exec db psql calendar_db db_user

tdb:
	docker-compose $(compose_config) exec db psql calendar_test_db test_db_user

migrate:
	docker-compose $(compose_config) exec $(container) poetry run alembic upgrade head

tmigrate:
	docker-compose $(compose_config) exec $(container) /bin/sh -c "$(test_env) poetry run alembic upgrade head"

rollback:
	docker-compose $(compose_config) exec $(container) poetry run alembic downgrade -1

trollback:
	docker-compose $(compose_config) exec $(container) /bin/sh -c "$(test_env) poetry run alembic downgrade -1"

####################################################

# start the docker VM
mt:
	docker-machine start

# stop the docker VM
mp:
	docker-machine stop

# clear every unused asset
cl:
	docker system prune -a --volumes
