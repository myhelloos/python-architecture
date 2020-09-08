#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/3 6:17 PM
@desc:
"""
from datetime import date
from unittest import mock

import pytest

from allocation.domain import model, events, commands
from allocation.adapters import repository
from allocation.service_layer import handlers, unit_of_work, messagebus


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


class TestAddBatch:

    def test_add_batch_for_new_product(self):
        uow = FakeUnitOfWork()

        messagebus.handle(
            commands.CreateBatch('b1', 'CRUNCHY-ARMCHAIR', 100, None)
            , uow
        )

        assert uow.products.get('CRUNCHY-ARMCHAIR') is not None
        assert uow.committed is True

    def test_add_batch_for_existing_product(self):
        uow = FakeUnitOfWork()

        messagebus.handle(
            commands.CreateBatch('b1', 'GARISH-RUG', 100, None)
            , uow
        )
        messagebus.handle(
            commands.CreateBatch('b2', 'GARISH-RUG', 99, None)
            , uow
        )

        assert 'b2' in [b.reference for b in uow.products.get('GARISH-RUG').batches]


class TestAllocate:
    def test_returns_allocation(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            commands.CreateBatch('b1', 'COMPLICATED-LAMP', 100, None)
            , uow
        )

        results = messagebus.handle(
            commands.Allocate('o1', 'COMPLICATED-LAMP', 10)
            , uow
        )

        assert results.pop(0) == 'b1'

    def test_error_for_invalid_sku(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            commands.CreateBatch('b1', 'AREALSKU', 100, None)
            , uow
        )

        with pytest.raises(handlers.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
            messagebus.handle(
                commands.Allocate("o1", "NONEXISTENTSKU", 10)
                , uow
            )

    def test_commits(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            commands.CreateBatch('b1', 'OMINOUS-MIRROR', 100, None)
            , uow
        )

        messagebus.handle(
            commands.Allocate('o1', 'OMINOUS-MIRROR', 10)
            , uow
        )

        assert uow.committed is True

    def test_sends_email_on_out_of_stock_error(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            commands.CreateBatch('b1', 'POPULAR-CURTAINS', 9, None)
            , uow
        )

        with mock.patch('allocation.adapters.email.send_mail') as mock_send_email:
            messagebus.handle(
                commands.Allocate('o1', 'POPULAR-CURTAINS', 10)
                , uow
            )

            assert mock_send_email.call_args == mock.call(
                "stock@made.com"
                , f"Out of stock for POPULAR-CURTAINS"
            )


class TestChangeBatchQuantity:
    def test_changes_available_quantity(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            commands.CreateBatch('batch1', 'ADORABLE-SETTEE', 100)
            , uow
        )
        [batch] = uow.products.get(sku='ADORABLE-SETTEE').batches
        assert batch.available_quantity == 100

        messagebus.handle(commands.ChangeBatchQuantity('batch1', 50), uow)
        assert batch.available_quantity == 50

    def test_reallocates_if_necessary(self):
        uow = FakeUnitOfWork()
        event_history = [
            commands.CreateBatch('batch1', 'INDIFFERENT-TABLE', 50, None)
            , commands.CreateBatch('batch2', 'INDIFFERENT-TABLE', 50, date.today())
            , commands.Allocate('order1', 'INDIFFERENT-TABLE', 20)
            , commands.Allocate('order2', 'INDIFFERENT-TABLE', 20)
        ]

        for e in event_history:
            messagebus.handle(e, uow)

        [batch1, batch2] = uow.products.get(sku='INDIFFERENT-TABLE').batches
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        messagebus.handle(commands.ChangeBatchQuantity('batch1', 25), uow)
        # order 1 and order2 will be deallocated, so we'll have 25 - 20
        assert batch1.available_quantity == 5
        # and 20 will be reallocated to the next batch
        assert batch2.available_quantity == 30