#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/3 6:17 PM
@desc:
"""
import pytest

from allocation.domain import model
from allocation.adapters import repository
from allocation.service_layer import services, unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self.__batches = set(batches)

    def add(self, batch: model.Batch):
        self.__batches.add(batch)

    def get(self, reference) -> model.Batch:
        return next(b for b in self.__batches if b.reference == reference)

    def list(self):
        return list(self.__batches)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
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


def test_add_batch():
    uow = FakeUnitOfWork()

    services.add_batch('b1', 'CRUNCHY-ARMCHAIR', 100, None, uow)

    assert uow.batches.get('b1') is not None
    assert uow.committed is True
