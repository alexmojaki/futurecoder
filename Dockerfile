# Stage 1 - Build frontend
FROM node:14.15.4 as build-frontend
WORKDIR /usr/src/app
COPY frontend/package-lock.json frontend/package.json ./frontend/

WORKDIR frontend
RUN npm ci
COPY frontend .
RUN npm run build
WORKDIR build
RUN sed -i s:/static/:/static_backend/:g index.html
RUN sed -i 's:"static/js/:"static_backend/js/:g' static/js/*

# Stage 2 - Setup server
FROM ubuntu:20.04

RUN apt-get update

RUN apt-get install -y software-properties-common curl
RUN (cd /etc/apt/trusted.gpg.d/ && curl -O https://www.postgresql.org/media/keys/ACCC4CF8.asc)
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)"-pgdg main >  /etc/apt/sources.list.d/pgdg.list
RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3.9-dev \
    vim \
    python3.9-distutils \
    gcc \
    postgresql-client-12 \
    git \
    zip \
    libpq-dev

RUN ln -s /usr/bin/python3.9 /usr/local/bin/python
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py
RUN pip install poetry

WORKDIR /usr/src/app
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN LC_ALL=C.UTF-8 LANG=C.UTF-8 poetry install --extras "production" --no-dev

COPY --from=build-frontend /usr/src/app/frontend/build ./frontend/build
COPY ./backend ./backend
WORKDIR /usr/src/app/backend
RUN mv /usr/lib/python3/dist-packages/six.py /usr/local/lib/python3.9/dist-packages/six.py
RUN ./package.sh
RUN ./manage.py compilescss
RUN ./manage.py collectstatic --noinput

EXPOSE 3000

CMD ["bash", "./entrypoint.sh"]
