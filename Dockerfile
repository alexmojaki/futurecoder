# Stage 1 - Build frontend
FROM node:12 as build-frontend
WORKDIR /usr/src/app
COPY frontend/package-lock.json frontend/package.json ./frontend/

WORKDIR frontend
RUN npm ci
COPY frontend .
RUN npm run build

# Stage 2 - Setup server
FROM ubuntu:18.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3.8-dev \
    unzip \
    nginx \
    curl \
    vim \
    python3.8-distutils \
    gcc

RUN ln -s /usr/bin/python3.8 /usr/local/bin/python
RUN python --version
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py
RUN pip --version
RUN pip install poetry

RUN apt-get install -y software-properties-common
RUN (cd /etc/apt/trusted.gpg.d/ && curl -O https://www.postgresql.org/media/keys/ACCC4CF8.asc)
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)"-pgdg main >  /etc/apt/sources.list.d/pgdg.list
RUN apt-get update -y
RUN apt-get install -y postgresql-client-12 libpq-dev

#RUN curl -s https://packagecloud.io/install/repositories/rabbitmq/rabbitmq-server/script.deb.sh | bash

WORKDIR /usr/src/app
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN LC_ALL=C.UTF-8 LANG=C.UTF-8 poetry install --extras "production" --no-dev

COPY --from=build-frontend /usr/src/app/frontend/build ./frontend/build
COPY ./backend ./backend
WORKDIR /usr/src/app/backend
RUN ./manage.py collectstatic --noinput

COPY ./backend/nginx.conf /etc/nginx

EXPOSE 3000

CMD ["bash", "./entrypoint.sh"]
