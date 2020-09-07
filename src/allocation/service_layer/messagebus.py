#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020-09-06 23:01
@desc:
"""
from typing import Dict, Type, List, Callable

from allocation.adapters import email
from allocation.domain import events
from allocation.service_layer import unit_of_work, handlers


def handle(
        event: events.Event
        , uow: unit_of_work.AbstractUnitOfWork
):
    queue = [event]

    results = []
    while queue:
        event = queue.pop(0)

        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow=uow))
            queue.extend(uow.collect_new_events())

    return results


HANDLERS = {
    events.OutOfStock: [handlers.send_out_of_stock_notification]
    , events.BatchCreated: [handlers.add_batch]
    , events.AllocationRequired: [handlers.allocate]
}  # type: Dict[Type[events.Event], List[Callable]]
