#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@file: test_services.py
@time: 2020/9/3 6:17 PM
@desc:
"""
import model
import repository


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self.__batches = set(batches)

    def add(self, batch: model.Batch):
        self.__batches.add(batch)

    def get(self, reference) -> model.Batch:
        return next(b for b in self.__batches if b.reference == reference)

    def list(self):
        return list(self.__batches)
