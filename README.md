# mycalendar
This a project app for the BME MSc class called "Software architectures" 

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
