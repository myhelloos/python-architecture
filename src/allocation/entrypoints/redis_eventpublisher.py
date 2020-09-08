#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/8 6:11 PM
@desc:
"""
import json
import logging
from dataclasses import asdict

import redis
from allocation import config
from allocation.domain import events

r = redis.Redis(**config.get_redis_host_and_port())
logger = logging.getLogger(__name__)


def publish(channel, event: events.Event):
    logger.debug('publishing: channel=%s, event=%s', channel, event)
    r.publish(channel, json.dumps(asdict(event)))
