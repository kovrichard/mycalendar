.PHONY: build start stop restart sh logs config lint mstart mstop clear

# \
!ifdef USE_LEGACY_DOCKER # \
compose_config=-f docker-compose.yml -f docker-compose-legacy.yml # \
!else
compose_config=-f docker-compose.yml
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

# run tests
test:
	docker-compose $(compose_config) exec $(container) /bin/sh -c "poetry run nose2 -v"

# check console output
logs:
	docker-compose $(compose_config) logs -f

# show the combined compose file used
config:
	docker-compose $(compose_config) config

# lint code
lint:
	docker-compose $(compose_config) exec $(container) poetry run isort mycalendar tests
	docker-compose $(compose_config) exec $(container) poetry run black mycalendar tests

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
