#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@file: config.py
@time: 2020/9/3 11:10 AM
@desc:
"""
import os


def get_postgres_uri():
    host = os.environ.get('DB_HOST', 'localhost')
    port = 54321 if host == 'localhost' else 5432
    password = os.environ.get('DB_PASSWORD', 'abc123')
    user, db_name = 'allocation', 'allocation'
    return f'postgresql://{user}:{password}@{host}:{port}/{db_name}'


def get_api_url():
    host = os.environ.get('API_HOST', 'localhost')
    port = 5005 if host == 'localhost' else 80
    return f'http://{host}:{port}'
