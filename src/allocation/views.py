#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/9 12:39 PM
@desc:
"""
from allocation.service_layer import unit_of_work


def allocations(orderid: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        results = list(uow.session.execute(
            'SELECT sku, batchref FROM allocations_view WHERE orderid = :orderid'
            , dict(orderid=orderid)
        ))

    return [dict(r) for r in results]
