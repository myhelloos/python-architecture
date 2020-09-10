#!/usr/bin/env python
# encoding: utf-8
# pylint: disable=unused-argument
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@file: handlers.py
@time: 2020/9/4 11:17 AM
@desc:
"""
from __future__ import annotations
from dataclasses import asdict
from typing import TYPE_CHECKING, Callable

from allocation.domain import model, events, commands

if TYPE_CHECKING:
    from allocation.adapters import notifications
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
        , notifications: notifications.AbstractNotifications
):
    notifications.send(
        'stock@made.com'
        , f'Out of stock for {event.sku}'
    )


def change_batch_quantity(
        command: commands.ChangeBatchQuantity
        , uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get_by_batchref(batchref=command.ref)
        product.change_batch_quantity(ref=command.ref, qty=command.qty)
        uow.commit()


def publish_allocated_event(
        event: events.Allocated
        , publish: Callable
):
    publish('line_allocated', event)


def add_allocation_to_read_model(
        event: events.Allocated
        , update_readmodel: Callable
):
    update_readmodel(event.orderid, event.sku, event.batchref)


def reallocate(
        event: events.Deallocated
        , uow: unit_of_work.AbstractUnitOfWork
):
    allocate(commands.Allocate(**asdict(event)), uow=uow)


def remove_allocation_from_read_model(
        event: events.Deallocated
        , update_readmodel: Callable
):
    update_readmodel(event.orderid, event.sku, None)


EVENT_HANDLERS = {
    events.OutOfStock: [send_out_of_stock_notification]
    , events.Allocated: [publish_allocated_event, add_allocation_to_read_model]
    , events.Deallocated: [remove_allocation_from_read_model, reallocate]
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.CreateBatch: add_batch
    , commands.Allocate: allocate
    , commands.ChangeBatchQuantity: change_batch_quantity
}  # type: Dict[Type[commands.Command], Callable]
