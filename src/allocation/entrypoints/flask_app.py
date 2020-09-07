#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@file: flask_app.py
@time: 2020/9/3 11:55 AM
@desc:
"""
from datetime import datetime

from allocation.adapters import orm
from allocation.service_layer import handlers, unit_of_work
from flask import Flask, request, jsonify

app = Flask(__name__)
orm.start_mappers()


@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    try:
        batchref = handlers.allocate(
            request.json['orderid']
            , request.json['sku']
            , request.json['qty']
            , unit_of_work.SqlAlchemyUnitOfWork()
        )
    except handlers.InvalidSku as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchref': batchref}), 201


@app.route('/batches', methods=['POST'])
def add_stock():
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()

    handlers.add_batch(
        request.json['ref']
        , request.json['sku']
        , request.json['qty']
        , eta
        , unit_of_work.SqlAlchemyUnitOfWork()
    )

    return 'OK', 201
