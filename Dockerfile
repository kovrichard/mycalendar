FROM python:3.8.3-alpine

RUN apk update && apk upgrade
RUN apk add --no-cache --virtual .build-deps curl gcc musl-dev

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python && \
    ln -s /root/.poetry/bin/poetry /usr/local/bin/poetry

WORKDIR /usr/src/app

COPY . /usr/src/app/
RUN poetry install && \
    rm -rf /usr/src/app/*

RUN apk --purge del .build-deps
