# mycalendar
This a project app for the BME MSc class called "[Software Architectures](https://www.aut.bme.hu/Course/VIAUMA06)".  
  
You can find this running application to click here: https://szoftarch-calendar.herokuapp.com.

## Installation & Usage
###### There are various installation and usage methods. Here is one of them. 
#### Windows 10 
  1. Download and install [Docker Desktop](https://hub.docker.com/editions/community/docker-ce-desktop-windows/).
  2. Download [Build Tools for Visual Studio 2019](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019) and under `C++ build tools` install only `MSVC v... -VS 2019 C++ ... build tools`. (This contains the Cross Tools Command Prompt for VS 2019.)
  3. Download (and extract) or clone the `mycalendar` repository.
  4. Run the downloaded `Docker Desktop` program. 
  5. Run `Cross Tools Command Prompt for VS 2019` program and `cd` into the local repository folder. Then give to the following commands:
     * `docker network create szoftarch`
     * `nmake build`
     * `nmake start`
     * `nmake migrate`
  6. (To test the code:)
     * `nmake lint`
     * `nmake test`
  7. Open any browser and in the URL field type: `localhost`.

# prerequisites for development
- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

Install these and you are good to go. All development happens within the container.

`Dockerfile` describes the container for the app. `docker-compose.yml` describes the environment outside of the app container, like DBs, queues, etc.

# prerequisites for older OS versions
- [Docker Toolbox](https://docs.docker.com/toolbox/)
- set `USE_LEGACY_DOCKER` environment variable to `1`

`docker-compose-legacy.yml` is used, when the host machine runs an older version of Docker via boot2docker. For this to work, the root of this repository must be added as a shared folder to the VM. Name the folder **mycalendar** and check **Auto-mount** and **Make Permanent** if you are using VirtualBox.

On older machines - instead of localhost - the app will be available on a different IP, which is assigned to Docker Toolbox on start. To get this IP, type `docker-machine ip`.

# network
The calendar and the database communicate through a network called `szoftarch`. This needs to be created once.

Create it by: `docker network create szoftarch`

# how to run
Using `make`. Check out the `Makefile`. The most important Docker commands (like building, starting and stopping a container) are described here. For Windows, there is [NMake](https://docs.microsoft.com/en-us/cpp/build/reference/nmake-reference?view=vs-2019).

```
make start
```

## get nmake.exe
Download `Build Tools for Visual Studio 2019` from [Microsoft's VS site](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019). Install only `MSVC ... build tools ` under `C++ build tools`.

# dependencies
Dependencies are managed via `poetry`. To manage dependencies always connect to the container (`make sh`)  first and run poetry within.

To add a new package use `poetry add [package-name]`.

# database
The project uses Postgresql with SQLAlchemy as an ORM and Alembic to handle migrations.

Migrations are stored under `alembic/versions`.

To get a completely clean postgres database, delete the `database-data` docker volume. Find it by running `docker volume ls`, delete it by running `docker volume rm [project]_database-data`.

## to get a db console
```
make db
make tdb # for test db
```

## to migrate to the latest schema
```
make migrate
make tmigrate # for test db
```

## to rollback one migration
```
make rollback
make trollback # for test tb
```

## to create a new migration
Edit the model first (or create new models), and then run the following script.

```
make sh
poetry run alembic revision --autogenerate -m "[description]"
```

Adjust the generated migration if needed.

### to check a migration
```
make sh
poetry run alembic upgrade --sql head
```

