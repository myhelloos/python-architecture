#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Node Supply Chain Manager Corporation Limited.
@file: orm.py
@time: 2020/9/2 11:27 AM
@desc: the orm
"""
from sqlalchemy import MetaData, Table, Column, Integer, String, Date
from sqlalchemy.orm import mapper
import model

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
    , Column('reference', String(255), primary_key=True)
    , Column('sku', String(255), primary_key=True)
    , Column('_purchased_quantity', Integer)
    , Column('eta', Date)
)


def start_mappers():
    mapper(model.OrderLine, order_lines)
    mapper(model.Batch, batches)
