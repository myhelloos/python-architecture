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

from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from src.allocation.domain import model
from src.allocation.adapters import repository, orm
from src.allocation.service_layer import services

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)

    try:
        batchref = services.allocate(
            request.json['orderid']
            , request.json['sku']
            , request.json['qty']
            , repo
            , session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchref': batchref}), 201


@app.route('/batches', methods=['POST'])
def add_stock():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)

    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()

    services.add_batch(
        request.json['ref']
        , request.json['sku']
        , request.json['qty']
        , eta
        , repo
        , session
    )

    return 'OK', 201
