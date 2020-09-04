#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Node Supply Chain Manager Corporation Limited.
@file: orm.py
@time: 2020/9/2 11:27 AM
@desc: the orm
"""
from sqlalchemy import MetaData, Table, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import mapper, relationship
from domain import model

metadata = MetaData()

order_lines = Table(
    'order_lines'
    , metadata
    , Column('id', Integer, primary_key=True, autoincrement=True)
    , Column('sku', String(255))
    , Column('qty', Integer, nullable=False)
    , Column('orderid', String(255))
)

batches = Table(
    'batches'
    , metadata
    , Column('id', Integer, primary_key=True, autoincrement=True)
    , Column('reference', String(255))
    , Column('sku', String(255))
    , Column('_purchased_quantity', Integer, nullable=False)
    , Column('eta', Date, nullable=True)
)

allocations = Table(
    'allocations'
    , metadata
    , Column('id', Integer, primary_key=True, autoincrement=True)
    , Column('orderline_id', ForeignKey('order_lines.id'))
    , Column('batch_id', ForeignKey('batches.id'))
)


def start_mappers():
    line_mapper = mapper(model.OrderLine, order_lines)
    mapper(
        model.Batch
        , batches
        , properties={'_allocations': relationship(
            line_mapper
            , secondary=allocations
            , collection_class=set
        )})
