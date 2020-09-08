#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/8 6:59 PM
@desc:
"""
import json

import redis
from allocation import config

r = redis.Redis(**config.get_redis_host_and_port())


def subscribe_to(channel):
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    confirmation = pubsub.get_message(timeout=3)
    assert confirmation['type'] == 'subscribe'
    return pubsub


def publish_message(channel, message):
    r.publish(channel, json.dumps(message))
