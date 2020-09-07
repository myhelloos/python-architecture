#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@file: handlers.py
@time: 2020/9/4 11:17 AM
@desc:
"""
from datetime import date
from typing import Optional, TYPE_CHECKING

from allocation.adapters import email
from allocation.domain import model, events

from . import unit_of_work


class InvalidSku(Exception):
    pass


def allocate(
        event: events.AllocationRequired
        , uow: unit_of_work.AbstractUnitOfWork
) -> str:
    with uow:
        product = uow.products.get(sku=event.sku)

        if product is None:
            raise InvalidSku(f'Invalid sku {event.sku}')

        line = model.OrderLine(event.orderid, event.sku, event.qty)
        batch_ref = product.allocate(line)
        uow.commit()
        return batch_ref


def add_batch(
        event: events.BatchCreated
        , uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get(sku=event.sku)

        if product is None:
            product = model.Product(event.sku, batches=[])
            uow.products.add(product)

        product.batches.append(model.Batch(event.ref, event.sku, event.qty, event.eta))
        uow.commit()


def send_out_of_stock_notification(
        event: events.OutOfStock
        , uow: unit_of_work.AbstractUnitOfWork
):
    email.send_mail(
        'stock@made.com'
        , f'Out of stock for {event.sku}'
    )
