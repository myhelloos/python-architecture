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
from allocation import views
from allocation.domain import commands
from allocation.service_layer import unit_of_work, messagebus

today = date.today()


@pytest.mark.usefixtures('cleanup_redis')
def test_allocations_view(sqlite_session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    messagebus.handle(commands.CreateBatch('sku1batch', 'sku1', 50, None), uow)
    messagebus.handle(commands.CreateBatch('sku2batch', 'sku2', 50, today), uow)
    messagebus.handle(commands.Allocate('order1', 'sku1', 20), uow)
    messagebus.handle(commands.Allocate('order1', 'sku2', 20), uow)
    # add s spurious batch and order to make sure we're getting the right ones
    messagebus.handle(commands.CreateBatch('sku1batch-later', 'sku1', 50, today), uow)
    messagebus.handle(commands.Allocate('otherorder', 'sku1', 30), uow)
    messagebus.handle(commands.Allocate('otherorder', 'sku2', 10), uow)

    assert views.allocations('order1') == [
        {'sku': 'sku1', 'batchref': 'sku1batch'}
        , {'sku': 'sku2', 'batchref': 'sku2batch'}
    ]


@pytest.mark.usefixtures('cleanup_redis')
def test_deallocation(sqlite_session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    messagebus.handle(commands.CreateBatch('b1', 'sku1', 50, None), uow)
    messagebus.handle(commands.CreateBatch('b2', 'sku1', 50, today), uow)
    messagebus.handle(commands.Allocate('o1', 'sku1', 40), uow)
    messagebus.handle(commands.ChangeBatchQuantity('b1', 10), uow)

    assert views.allocations('o1') == [
        {'sku': 'sku1', 'batchref': 'b2'}
    ]
