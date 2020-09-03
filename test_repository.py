#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Node Supply Chain Manager Corporation Limited.
@file: test_repository.py
@time: 2020/9/2 12:59 PM
@desc:
"""
import model
import repository


def test_repository_can_save_a_batch(session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = list(session.execute('SELECT reference, sku, _purchased_quantity, eta FROM "batches"'))
    assert rows == [("batch1", "RUSTY-SOAPDISH", 100, None)]


def __insert_order_line(session):
    session.execute(
        'INSERT INTO order_lines (orderid, sku, qty)'
        ' VALUES ("order1", "GENERIC-SOFA", 12)'
    )

    [[orderline_id]] = session.execute(
        'SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku'
        , dict(orderid="order1", sku="GENERIC-SOFA")
    )

    return orderline_id


def __insert_batch(session, batch_id):
    session.execute(
        'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        ' VALUES (:batch_id, "GENERIC-SOFA", 100, null)'
        , dict(batch_id=batch_id)
    )

    [[batch_id]] = session.execute(
        'SELECT id FROM batches WHERE reference=:batch_id AND sku="GENERIC-SOFA"'
        , dict(batch_id=batch_id)
    )

    return batch_id


def __insert_allocation(session, orderline_id, batch_id):
    session.execute(
        'INSERT INTO allocations (orderline_id, batch_id)'
        ' VALUES (:orderline_id, :batch_id)'
        , dict(orderline_id=orderline_id, batch_id=batch_id)
    )


def test_repository_can_retrieve_a_batch_with_allocations(session):
    orderline_id = __insert_order_line(session)
    batch_id = __insert_batch(session, 'batch-1')
    __insert_batch(session, 'batch-2')
    __insert_allocation(session, orderline_id, batch_id)

    repo = repository.SqlAlchemyRepository(session)
    retrived = repo.get('batch-1')

    expected = model.Batch('batch-1', "GENERIC-SOFA", 100, eta=None)
    assert retrived == expected
    # Batch.__eq__ only compares reference
    assert retrived.sku == expected.sku
    assert retrived._purchased_quantity == expected._purchased_quantity
    assert retrived._allocations == {model.OrderLine("order1", "GENERIC-SOFA", 12)}
