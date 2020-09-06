#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/3 6:17 PM
@desc:
"""
from unittest import mock

import pytest

from allocation.domain import model
from allocation.adapters import repository
from allocation.service_layer import services, unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products: [model.Product]):
        super().__init__()
        self.__products = set(products)

    def _add(self, product: model.Product):
        self.__products.add(product)

    def _get(self, sku) -> model.Product:
        return next((p for p in self.__products if p.sku == sku), None)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'COMPLICATED-LAMP', 100, None, uow)

    result = services.allocate('o1', 'COMPLICATED-LAMP', 10, uow)

    assert result == 'b1'


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'AREALSKU', 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_commits():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'OMINOUS-MIRROR', 100, None, uow)

    services.allocate('o1', 'OMINOUS-MIRROR', 10, uow)

    assert uow.committed is True


def test_add_batch_for_new_product():
    uow = FakeUnitOfWork()

    services.add_batch('b1', 'CRUNCHY-ARMCHAIR', 100, None, uow)

    assert uow.products.get('CRUNCHY-ARMCHAIR') is not None
    assert uow.committed is True


def test_add_batch_for_existing_product():
    uow = FakeUnitOfWork()

    services.add_batch('b1', 'GARISH-RUG', 100, None, uow)
    services.add_batch('b2', 'GARISH-RUG', 99, None, uow)

    assert 'b2' in [b.reference for b in uow.products.get('GARISH-RUG').batches]


def test_sends_email_on_out_of_stock_error():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'POPULAR-CURTAINS', 9, None, uow)

    with mock.patch('allocation.adapters.email.send_mail') as mock_send_email:
        services.allocate('o1', 'POPULAR-CURTAINS', 10, uow)

        assert mock_send_email.call_args == mock.call(
            "stock@made.com"
            , f"Out of stock for POPULAR-CURTAINS"
        )
