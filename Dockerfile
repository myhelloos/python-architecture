FROM python:3.8-alpine

COPY repositories /etc/apk/repositories
RUN apk update && apk add vim curl net-tools lua

RUN apk add --no-cache --virtual .build-deps gcc postgresql-dev musl-dev python3-dev
RUN apk add libpq

RUN pip install -U pip
RUN pip config set global.index-url https://mirrors.ustc.edu.cn/pypi/web/simple
RUN pip config set install.trusted-host mirrors.ustc.edu.cn

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

RUN apk del --no-cache .build-deps

RUN mkdir -p /code
COPY *.py /code/
WORKDIR /code
ENV FLASK_APP=flask_app.py FLASK_DEBUG=1 PYTHONUNBUFFERED=1
CMD flask run --host=0.0.0.0 --port=80
