#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/3 11:35 AM
@desc:
"""

import pytest
import requests
from allocation import config

from ..random_refs import random_sku, random_batchref, random_orderid


def post_to_add_batch(ref, sku, qty, eta):
    url = config.get_api_url()

    r = requests.post(
        f'{url}/batches'
        , json={'ref': ref, 'sku': sku, 'qty': qty, 'eta': eta}
    )

    assert r.status_code == 201


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_happy_path_returns_201_and_allocated_batch():
    sku, other_sku = random_sku(), random_sku('other')
    early_batch = random_batchref(1)
    later_batch = random_batchref(2)
    other_batch = random_batchref(3)

    post_to_add_batch(later_batch, sku, 100, '2011-01-02')
    post_to_add_batch(early_batch, sku, 100, '2011-01-01')
    post_to_add_batch(other_batch, other_sku, 100, None)

    data = {'orderid': random_orderid(), 'sku': sku, 'qty': 3}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)

    assert r.status_code == 201
    assert r.json()['batchref'] == early_batch


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, order_id = random_sku(), random_orderid()

    data = {'orderid': order_id, 'sku': unknown_sku, 'qty': 10}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)

    assert r.status_code == 400
    assert r.json()['message'] == f'Invalid sku {unknown_sku}'
