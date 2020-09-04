#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/3 6:17 PM
@desc:
"""
import pytest

from domain import model
from adapters import repository
from service_layer import services


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self.__batches = set(batches)

    def add(self, batch: model.Batch):
        self.__batches.add(batch)

    def get(self, reference) -> model.Batch:
        return next(b for b in self.__batches if b.reference == reference)

    def list(self):
        return list(self.__batches)

    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return model.Batch(ref, sku, qty, eta)


class FakeSession():
    commited = False

    def commit(self):
        self.commited = True


def test_returns_allocation():
    batch = FakeRepository.for_batch('b1', 'COMPLICATED-LAMP', 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate('o1', 'COMPLICATED-LAMP', 10, repo, FakeSession())

    assert result == 'b1'


def test_error_for_invalid_sku():
    batch = FakeRepository.for_batch('b1', 'AREALSKU', 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_commits():
    batch = FakeRepository.for_batch('b1', 'OMINOUS-MIRROR', 100)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate('o1', 'OMINOUS-MIRROR', 10, repo, session)

    assert session.commited is True
