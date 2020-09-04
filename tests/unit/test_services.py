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


class FakeSession():
    commited = False

    def commit(self):
        self.commited = True


def test_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'COMPLICATED-LAMP', 100, None, repo, session)

    result = services.allocate('o1', 'COMPLICATED-LAMP', 10, repo, session)

    assert result == 'b1'


def test_error_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'AREALSKU', 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, session)


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'OMINOUS-MIRROR', 100, None, repo, session)

    services.allocate('o1', 'OMINOUS-MIRROR', 10, repo, session)

    assert session.commited is True


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()

    services.add_batch('b1', 'CRUNCHY-ARMCHAIR', 100, None, repo, session)

    assert repo.get('b1') is not None
    assert session.commited is True
