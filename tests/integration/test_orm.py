#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Node Supply Chain Manager Corporation Limited.
@time: 2020/9/2 11:33 AM
@desc:
"""
from datetime import date

from domain import model


def test_orderline_mapper_can_load_lines(session):
    session.execute(
        'INSERT INTO order_lines (orderid, sku, qty) VALUES '
        '("order1", "RED-CHAIR", 12),'
        '("order1", "RED-TABLE", 13),'
        '("order2", "BLUE-LIPSTICK", 14)'
    )
    expected = [
        model.OrderLine("order1", "RED-CHAIR", 12)
        , model.OrderLine("order1", "RED-TABLE", 13)
        , model.OrderLine("order2", "BLUE-LIPSTICK", 14)
    ]
    assert session.query(model.OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(session):
    new_line = model.OrderLine("order1", "DECORATIVE-WIDGET", 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute('SELECT orderid, sku, qty FROM "order_lines"'))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]


def test_batches(session):
    session.execute(
        'INSERT INTO "batches" (reference, sku, _purchased_quantity, eta)'
        'VALUES ("batch1", "sku1", 100, null)')
    session.execute(
        'INSERT INTO "batches" (reference, sku, _purchased_quantity, eta)'
        'VALUES ("batch2", "sku2", 200, "2011-04-11")')

    expected = [
        model.Batch("batch1", "sku1", 100, eta=None)
        , model.Batch("batch2", "sku2", 200, eta=date(2011, 4, 11))
    ]

    assert session.query(model.Batch).all() == expected
