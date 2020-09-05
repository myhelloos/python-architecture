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


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
        orderid: str
        , sku: str
        , qty: int
        , uow: unit_of_work.AbstractUnitOfWork
) -> str:
    with uow:
        batches = uow.batches.list()

        if not is_valid_sku(sku, batches):
            raise InvalidSku(f'Invalid sku {sku}')

        line = model.OrderLine(orderid, sku, qty)
        batch_ref = model.allocate(line, batches)
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
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        uow.commit()
