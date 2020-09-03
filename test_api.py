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
def test_api_returns_allocation(add_stock):
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
def test_allocations_are_persisted(add_stock):
    sku = random_sku()
    batch_1, batch_2 = random_batchref(1), random_batchref(2)
    order_1, order_2 = random_orderid(1), random_orderid(2)

    add_stock([
        (batch_1, sku, 10, '2011-01-01')
        , (batch_2, sku, 10, '2011-01-02')
    ])

    line_1 = {'orderid': order_1, 'sku': sku, 'qty': 10}
    line_2 = {'orderid': order_2, 'sku': sku, 'qty': 10}

    url = config.get_api_url()

    r = requests.post(f'{url}/allocate', json=line_1)
    assert r.status_code == 201
    assert r.json()['batchref'] == batch_1

    r = requests.post(f'{url}/allocate', json=line_2)
    assert r.status_code == 201
    assert r.json()['batchref'] == batch_2
