#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@file: services.py
@time: 2020/9/4 11:17 AM
@desc:
"""
from datetime import date
from typing import Optional

from allocation.domain import model

from allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def allocate(
        orderid: str
        , sku: str
        , qty: int
        , uow: unit_of_work.AbstractUnitOfWork
) -> str:
    with uow:
        product = uow.products.get(sku=sku)

        if product is None:
            raise InvalidSku(f'Invalid sku {sku}')

        line = model.OrderLine(orderid, sku, qty)
        batch_ref = product.allocate(line)
        uow.commit()

    return batch_ref


def add_batch(
        ref: str
        , sku: str
        , qty: int
        , eta: Optional[date]
        , uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get(sku=sku)

        if product is None:
            product = model.Product(sku, batches=[])
            uow.products.add(product)

        product.batches.append(model.Batch(ref, sku, qty, eta))
        uow.commit()
