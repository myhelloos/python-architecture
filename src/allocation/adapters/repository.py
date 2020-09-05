#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Node Supply Chain Manager Corporation Limited.
@file: repository.py
@time: 2020/9/2 11:58 AM
@desc:
"""
import abc

from allocation.domain import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, product: model.Product):
        raise NotImplementedError

    def get(self, sku) -> model.Product:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        self.session = session

    def add(self, product: model.Product):
        self.session.add(product)

    def get(self, sku) -> model.Product:
        return self.session.query(model.Product).filter_by(sku=sku).first()
