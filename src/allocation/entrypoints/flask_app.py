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

from allocation import views, bootstrap
from allocation.domain import commands
from allocation.service_layer import handlers, unit_of_work
from flask import Flask, request, jsonify

app = Flask(__name__)
bus = bootstrap.bootstrap()


@app.route('/allocations/<orderid>', methods=['GET'])
def allocations_view_endpoint(orderid):
    result = views.allocations(orderid)

    if not result:
        return 'not found', 404
    return jsonify(result), 200


@app.route('/allocations', methods=['POST'])
def allocate_endpoint():
    try:
        command = commands.Allocate(
            request.json['orderid']
            , request.json['sku']
            , request.json['qty']
        )
        bus.handle(command)
    except handlers.InvalidSku as e:
        return jsonify({'message': str(e)}), 400

    return 'OK', 202


@app.route('/batches', methods=['POST'])
def add_stock():
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()

    command = commands.CreateBatch(
        request.json['ref']
        , request.json['sku']
        , request.json['qty']
        , eta
    )
    bus.handle(command)

    return 'OK', 201
