#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@file: test_api.py
@time: 2020/9/3 11:35 AM
@desc:
"""
import uuid

import pytest
import requests

import config


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=''):
    return f'sku-{name}-{random_suffix()}'


def random_batchref(name=''):
    return f'batch-{name}-{random_suffix()}'


def random_orderid(name=''):
    return f'order-{name}-{random_suffix()}'


@pytest.mark.usefixtures('restart_api')
def test_happy_path_returns_201_and_allocated_batch(add_stock):
    sku, other_sku = random_sku(), random_sku('other')
    early_batch = random_batchref(1)
    later_batch = random_batchref(2)
    other_batch = random_batchref(3)

    add_stock([
        (later_batch, sku, 100, '2011-01-02')
        , (early_batch, sku, 100, '2011-01-01')
        , (other_batch, other_sku, 100, None)
    ])

    data = {'orderid': random_orderid(), 'sku': sku, 'qty': 3}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)

    assert r.status_code == 201
    assert r.json()['batchref'] == early_batch


@pytest.mark.usefixtures('restart_api')
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, order_id = random_sku(), random_orderid()

    data = {'orderid': order_id, 'sku': unknown_sku, 'qty': 10}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)

    assert r.status_code == 400
    assert r.json()['message'] == f'Invalid sku {unknown_sku}'
