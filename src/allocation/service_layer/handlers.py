#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@file: handlers.py
@time: 2020/9/4 11:17 AM
@desc:
"""
from allocation.adapters import email
from allocation.domain import model, events, commands
from allocation.entrypoints import redis_eventpublisher

from . import unit_of_work


class InvalidSku(Exception):
    pass


def allocate(
        command: commands.Allocate
        , uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get(sku=command.sku)

        if product is None:
            raise InvalidSku(f'Invalid sku {command.sku}')

        line = model.OrderLine(command.orderid, command.sku, command.qty)
        product.allocate(line)

        uow.commit()


def add_batch(
        command: commands.CreateBatch
        , uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get(sku=command.sku)

        if product is None:
            product = model.Product(command.sku, batches=[])
            uow.products.add(product)

        product.batches.append(model.Batch(command.ref, command.sku, command.qty, command.eta))
        uow.commit()


def send_out_of_stock_notification(
        event: events.OutOfStock
        , uow: unit_of_work.AbstractUnitOfWork
):
    email.send_mail(
        'stock@made.com'
        , f'Out of stock for {event.sku}'
    )


def change_batch_qunatity(
        command: commands.ChangeBatchQuantity
        , uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get_by_batchref(batchref=command.ref)
        product.change_batch_quantity(ref=command.ref, qty=command.qty)
        uow.commit()


def publish_allocated_event(
        event: events.Allocated
        , uow: unit_of_work.AbstractUnitOfWork
):
    redis_eventpublisher.publish('line_allocated', event)
