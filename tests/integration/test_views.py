#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020-09-09 23:09
@desc:
"""
from datetime import date

import pytest
from allocation import views, bootstrap
from allocation.domain import commands
from allocation.entrypoints import redis_eventpublisher
from allocation.service_layer import unit_of_work
from sqlalchemy.orm import clear_mappers

today = date.today()


@pytest.fixture
def sqlite_bus(sqlite_session_factory):
    bus = bootstrap.bootstrap(
        start_orm=True
        , uow=unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
        , send_mail=lambda *args: None
        , publish=lambda *args: None
        , update_readmodel=redis_eventpublisher.update_readmodel
    )
    yield bus
    clear_mappers()


@pytest.mark.usefixtures('cleanup_redis')
def test_allocations_view(sqlite_bus):
    sqlite_bus.handle(commands.CreateBatch('sku1batch', 'sku1', 50, None))
    sqlite_bus.handle(commands.CreateBatch('sku2batch', 'sku2', 50, today))
    sqlite_bus.handle(commands.Allocate('order1', 'sku1', 20))
    sqlite_bus.handle(commands.Allocate('order1', 'sku2', 20))
    # add s spurious batch and order to make sure we're getting the right ones
    sqlite_bus.handle(commands.CreateBatch('sku1batch-later', 'sku1', 50, today))
    sqlite_bus.handle(commands.Allocate('otherorder', 'sku1', 30))
    sqlite_bus.handle(commands.Allocate('otherorder', 'sku2', 10))

    assert views.allocations('order1') == [
        {'sku': 'sku1', 'batchref': 'sku1batch'}
        , {'sku': 'sku2', 'batchref': 'sku2batch'}
    ]


@pytest.mark.usefixtures('cleanup_redis')
def test_deallocation(sqlite_bus):
    sqlite_bus.handle(commands.CreateBatch('b1', 'sku1', 50, None))
    sqlite_bus.handle(commands.CreateBatch('b2', 'sku1', 50, today))
    sqlite_bus.handle(commands.Allocate('o1', 'sku1', 40))
    sqlite_bus.handle(commands.ChangeBatchQuantity('b1', 10))

    assert views.allocations('o1') == [
        {'sku': 'sku1', 'batchref': 'b2'}
    ]
