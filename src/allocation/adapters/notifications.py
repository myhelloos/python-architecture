#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/10 3:08 PM
@desc:
"""
import abc
import smtplib

from allocation import config


class AbstractNotifications(abc.ABC):
    @abc.abstractmethod
    def send(self, destination, message):
        raise NotImplementedError


DEFAULT_HOST = config.get_email_host_and_port()['host']
DEFAULT_PORT = config.get_email_host_and_port()['port']


class EmailNotifications(AbstractNotifications):
    def __init__(self, smtp_host=DEFAULT_HOST, smtp_port=DEFAULT_PORT):
        self.server = smtplib.SMTP(smtp_host, port=smtp_port)
        self.server.noop()

    def send(self, destination, message):
        msg = f'Subject: allocation service notification\n{message}'
        self.server.sendmail(
            from_addr='allocations@example.com'
            , to_addrs=[destination]
            , msg=msg
        )
