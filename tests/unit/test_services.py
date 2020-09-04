#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@file: test_services.py
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
    batch = model.Batch('b1', 'COMPLICATED-LAMP', 100, eta=None)
    repo = FakeRepository([batch])

    line = model.OrderLine('o1', 'COMPLICATED-LAMP', 10)
    result = services.allocate(line, repo, FakeSession())

    assert result == 'b1'


def test_error_for_invalid_sku():
    batch = model.Batch('b1', 'AREALSKU', 100, eta=None)
    repo = FakeRepository([batch])

    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    batch = model.Batch('b1', 'OMINOUS-MIRROR', 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    line = model.OrderLine('01', 'OMINOUS-MIRROR', 10)
    services.allocate(line, repo, session)

    assert session.commited is True
