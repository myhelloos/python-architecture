#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/3 6:17 PM
@desc:
"""
from collections import defaultdict
from datetime import date

import pytest
from allocation import bootstrap

from allocation.domain import model, commands
from allocation.adapters import repository, notifications
from allocation.service_layer import handlers, unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products: [model.Product]):
        super().__init__()
        self.__products = set(products)

    def _add(self, product: model.Product):
        self.__products.add(product)

    def _get(self, sku) -> model.Product:
        return next((p for p in self.__products if p.sku == sku), None)

    def _get_by_batchref(self, batchref) -> model.Product:
        return next(
            (
                p for p in self.__products for b in p.batches
                if b.reference == batchref
            )
            , None
        )


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakeNotifications(notifications.AbstractNotifications):

    def __init__(self):
        self.sent = defaultdict(list)  # type: Dict[str, List[str]]

    def send(self, destination, message):
        self.sent[destination].append(message)


def bootstrap_test_app():
    return bootstrap.bootstrap(
        start_orm=False
        , uow=FakeUnitOfWork()
        , notifications=FakeNotifications()
        , publish=lambda *args: None
        , update_readmodel=lambda *args: None
    )


class TestAddBatch:

    def test_add_batch_for_new_product(self):
        bus = bootstrap_test_app()

        bus.handle(commands.CreateBatch('b1', 'CRUNCHY-ARMCHAIR', 100, None))

        assert bus.uow.products.get('CRUNCHY-ARMCHAIR') is not None
        assert bus.uow.committed is True

    def test_add_batch_for_existing_product(self):
        bus = bootstrap_test_app()

        bus.handle(commands.CreateBatch('b1', 'GARISH-RUG', 100, None))
        bus.handle(commands.CreateBatch('b2', 'GARISH-RUG', 99, None))

        assert 'b2' in [b.reference for b in bus.uow.products.get('GARISH-RUG').batches]


class TestAllocate:
    @pytest.mark.usefixtures('cleanup_redis')
    def test_returns_allocation(self):
        bus = bootstrap_test_app()

        bus.handle(commands.CreateBatch('b1', 'COMPLICATED-LAMP', 100, None))

        bus.handle(commands.Allocate('o1', 'COMPLICATED-LAMP', 10))

        [batch] = bus.uow.products.get('COMPLICATED-LAMP').batches
        assert batch.available_quantity == 90

    @pytest.mark.usefixtures('cleanup_redis')
    def test_error_for_invalid_sku(self):
        bus = bootstrap_test_app()

        bus.handle(commands.CreateBatch('b1', 'AREALSKU', 100, None))

        with pytest.raises(handlers.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
            bus.handle(commands.Allocate("o1", "NONEXISTENTSKU", 10))

    @pytest.mark.usefixtures('cleanup_redis')
    def test_commits(self):
        bus = bootstrap_test_app()

        bus.handle(commands.CreateBatch('b1', 'OMINOUS-MIRROR', 100, None))

        bus.handle(commands.Allocate('o1', 'OMINOUS-MIRROR', 10))

        assert bus.uow.committed is True

    @pytest.mark.usefixtures('cleanup_redis')
    def test_sends_email_on_out_of_stock_error(self):
        fake_notifications = FakeNotifications()

        bus = bootstrap.bootstrap(
            start_orm=False
            , uow=FakeUnitOfWork()
            , notifications=fake_notifications
            , publish=lambda *args: None
            , update_readmodel=lambda *args: None
        )

        bus.handle(commands.CreateBatch('b1', 'POPULAR-CURTAINS', 9, None))
        bus.handle(commands.Allocate('o1', 'POPULAR-CURTAINS', 10))

        assert fake_notifications.sent['stock@made.com'] == ["Out of stock for POPULAR-CURTAINS"]


class TestChangeBatchQuantity:
    def test_changes_available_quantity(self):
        bus = bootstrap_test_app()

        bus.handle(commands.CreateBatch('batch1', 'ADORABLE-SETTEE', 100))
        [batch] = bus.uow.products.get(sku='ADORABLE-SETTEE').batches
        assert batch.available_quantity == 100

        bus.handle(commands.ChangeBatchQuantity('batch1', 50))
        assert batch.available_quantity == 50

    @pytest.mark.usefixtures('cleanup_redis')
    def test_reallocates_if_necessary(self):
        bus = bootstrap_test_app()

        event_history = [
            commands.CreateBatch('batch1', 'INDIFFERENT-TABLE', 50, None)
            , commands.CreateBatch('batch2', 'INDIFFERENT-TABLE', 50, date.today())
            , commands.Allocate('order1', 'INDIFFERENT-TABLE', 20)
            , commands.Allocate('order2', 'INDIFFERENT-TABLE', 20)
        ]

        for e in event_history:
            bus.handle(e)

        [batch1, batch2] = bus.uow.products.get(sku='INDIFFERENT-TABLE').batches
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        bus.handle(commands.ChangeBatchQuantity('batch1', 25))
        # order 1 and order2 will be deallocated, so we'll have 25 - 20
        assert batch1.available_quantity == 5
        # and 20 will be reallocated to the next batch
        assert batch2.available_quantity == 30
