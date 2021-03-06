#!/usr/bin/env python
# encoding: utf-8
# pylint: disable=redefined-outer-name
"""
@author: alfred
@license: (C) Copyright 2019-2020, Node Supply Chain Manager Corporation Limited.
@file: conftest.py
@time: 2020/9/2 11:39 AM
@desc:
"""
import logging
import shutil
import subprocess
from pathlib import Path
import time

import pytest
import redis
import requests
from redis import RedisError
from requests.exceptions import RequestException
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, clear_mappers

from allocation import config
from allocation.adapters.orm import metadata, start_mappers

pytest.register_assert_rewrite('tests.e2e.api_client')


@pytest.fixture
def in_memory_db():
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlite_session_factory(in_memory_db):
    yield sessionmaker(bind=in_memory_db)


@pytest.fixture
def mappers():
    start_mappers()
    yield
    clear_mappers()


@pytest.fixture
def sqlite_session(sqlite_session_factory):
    return sqlite_session_factory()


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail('Postgres never came up')


@pytest.fixture(scope='session')
def postgres_db():
    engine = create_engine(config.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session_factory(postgres_db):
    yield sessionmaker(bind=postgres_db)


@pytest.fixture
def postgres_session(postgres_session_factory):
    return postgres_session_factory()


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()

    while time.time() < deadline:
        try:
            return requests.get(url)
        except RequestException:
            time.sleep(0.5)
    pytest.fail('API never came up')


@pytest.fixture
def restart_api():
    (Path(__file__).parent / '../src/allocation/entrypoints/flask_app.py').touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


def wait_for_redis_to_come_up():
    deadline = time.time() + 5
    r = redis.Redis(**config.get_redis_host_and_port())
    while time.time() < deadline:
        try:
            return r.ping()
        except RedisError:
            time.sleep(0.5)
    pytest.fail('Redis never came up')


@pytest.fixture
def restart_redis_pubsub():
    wait_for_redis_to_come_up()
    if not shutil.which('docker-compose'):
        print('skipping restart, assumes running in containers')
        return
    subprocess.run(
        ['docker-compose', 'restart', '-t', '0', 'redis_pubsub']
        , check=True
    )


@pytest.fixture
def cleanup_redis():
    r = redis.Redis(**config.get_redis_host_and_port())
    yield
    for k in r.keys():
        logging.info('cleaning up redis key', k)
        r.delete(k)
