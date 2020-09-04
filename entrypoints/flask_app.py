#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@file: flask_app.py
@time: 2020/9/3 11:55 AM
@desc:
"""
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from domain import model
from adapters import repository, orm
from service_layer import services

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)

    orderid = request.json['orderid']
    sku = request.json['sku']
    qty = request.json['qty']

    try:
        batchref = services.allocate(orderid, sku, qty, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchref': batchref}), 201
