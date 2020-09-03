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
from pathlib import Path
import time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from config import get_postgres_uri
from orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


@pytest.fixture(scope='session')
def postgres_db():
    engine = create_engine(get_postgres_uri())
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db):
    start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture
def add_stock(postgres_session):
    batches_add = set()
    skus_add = set()

    def __add_stock(lines):
        for ref, sku, qty, eta in lines:
            postgres_session.execute(
                'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
                ' VALUES (:ref, :sku, :qty, :eta)'
                , dict(ref=ref, sku=sku, qty=qty, eta=eta)
            )
            [[batch_id]] = postgres_session.execute(
                'SELECT id FROM batches WHERE reference=:ref AND sku=:sku'
                , dict(ref=ref, sku=sku)
            )
            batches_add.add(batch_id)
            skus_add.add(sku)
        postgres_session.commit()

    yield __add_stock

    for batch_id in batches_add:
        postgres_session.execute(
            'DELETE FROM allocations WHERE batch_id=:batch_id'
            , dict(batch_id=batch_id)
        )
        postgres_session.execute(
            'DELETE FROM batches WHERE id=:batch_id'
            , dict(batch_id=batch_id)
        )
    for sku in skus_add:
        postgres_session.execute(
            'DELETE FROM order_lines WHERE sku=:sku'
            , dict(sku=sku)
        )
    postgres_session.commit()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / 'flask_app.py').touch()
    time.sleep(0.3)