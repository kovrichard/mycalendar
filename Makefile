.PHONY: build start stop restart sh tsh logs config lint db tdb mstart mstop clear migrate tmigrate rollback trollback

# \
!ifndef 0 # \
test_env="DATABASE_URL=$$TEST_DATABASE_URL" # \
!else
test_env=DATABASE_URL=\$$TEST_DATABASE_URL
# \
!endif

container=mycalendar

# build the mycalendar container
build:
	docker-compose build

# start all the containers
start:
	docker-compose up -d

# stop all the containers
stop:
	docker-compose down

# restart the mycalendar container
restart: stop start

# get a shell within the app container
sh:
	docker-compose exec $(container) /bin/sh

tsh:
	docker-compose exec $(container) /bin/sh -c "$(test_env) sh"

# run tests
test:
	docker-compose exec $(container) /bin/sh -c "$(test_env) poetry run nose2 -v"

# check console output
logs:
	docker-compose logs -f

# show the combined compose file used
config:
	docker-compose config

# lint code
lint:
	docker-compose exec $(container) poetry run autoflake --remove-all-unused-imports --ignore-init-module-imports --in-place --recursive mycalendar tests alembic
	docker-compose exec $(container) poetry run isort mycalendar tests alembic
	docker-compose exec $(container) poetry run black mycalendar tests alembic

db:
	docker-compose exec db psql calendar_db db_user

tdb:
	docker-compose exec db psql calendar_test_db test_db_user

migrate:
	docker-compose exec $(container) poetry run alembic upgrade head

tmigrate:
	docker-compose exec $(container) /bin/sh -c "$(test_env) poetry run alembic upgrade head"

rollback:
	docker-compose exec $(container) poetry run alembic downgrade -1

trollback:
	docker-compose exec $(container) /bin/sh -c "$(test_env) poetry run alembic downgrade -1"
