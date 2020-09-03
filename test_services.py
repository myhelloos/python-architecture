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

import model
import repository
import services


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self.__batches = set(batches)

    def add(self, batch: model.Batch):
        self.__batches.add(batch)

    def get(self, reference) -> model.Batch:
        return next(b for b in self.__batches if b.reference == reference)

    def list(self):
        return list(self.__batches)


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
        result = services.allocate(line, repo, FakeSession())