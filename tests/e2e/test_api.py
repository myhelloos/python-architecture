#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/3 11:35 AM
@desc:
"""

import pytest

from . import api_client
from ..random_refs import random_sku, random_batchref, random_orderid


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_happy_path_returns_201_and_allocated_batch():
    sku, other_sku = random_sku(), random_sku('other')
    early_batch = random_batchref(1)
    later_batch = random_batchref(2)
    other_batch = random_batchref(3)

    api_client.post_to_add_batch(later_batch, sku, 100, '2011-01-02')
    api_client.post_to_add_batch(early_batch, sku, 100, '2011-01-01')
    api_client.post_to_add_batch(other_batch, other_sku, 100, None)

    r = api_client.post_to_allocate(random_orderid(), sku, qty=3)

    assert r.json()['batchref'] == early_batch


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, order_id = random_sku(), random_orderid()

    r = api_client.post_to_allocate(order_id, unknown_sku, qty=20, expect_success=False)

    assert r.status_code == 400
    assert r.json()['message'] == f'Invalid sku {unknown_sku}'
