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


def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)


def send_out_stock_notification(event: events.OutOfStock):
    email.send_mail(
        'stock@made.com'
        , f'Out of stock for {event.sku}'
    )


HANDLERS = {
    events.OutOfStock: [send_out_stock_notification]
}  # type: Dict[Type[events.Event], List[Callable]]
