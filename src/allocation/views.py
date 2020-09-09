#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/9 12:39 PM
@desc:
"""
from allocation.entrypoints import redis_eventpublisher


def allocations(orderid: str):
    batches = redis_eventpublisher.get_readmodel(orderid)
    return [
        {'batchref': b.decode(), 'sku': s.decode()} for s, b in batches.items()
    ]
