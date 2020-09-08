#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/8 6:05 PM
@desc:
"""
import json
import logging

import redis
from allocation import config
from allocation.adapters import orm
from allocation.domain import commands
from allocation.service_layer import messagebus, unit_of_work

r = redis.Redis(**config.get_redis_host_and_port())
logger = logging.getLogger(__name__)


def handle_change_batch_quantity(m):
    logger.debug('handing %s', m)
    data = json.loads(m['data'])
    command = commands.ChangeBatchQuantity(ref=data['batchref'], qty=data['qty'])
    messagebus.handle(command, uow=unit_of_work.SqlAlchemyUnitOfWork())


def main():
    orm.start_mappers()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('change_batch_quantity')

    for m in pubsub.listen():
        handle_change_batch_quantity(m)
