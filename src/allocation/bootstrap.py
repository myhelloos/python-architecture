#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020/9/10 10:44 AM
@desc:
"""
import inspect
from typing import Callable

from allocation.adapters import email, orm
from allocation.entrypoints import redis_eventpublisher
from allocation.service_layer import unit_of_work, messagebus, handlers


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items() if name in params
    }
    return lambda message: handler(message, **deps)


def bootstrap(
        start_orm: bool = True
        , uow: unit_of_work.AbstractUnitOfWork = unit_of_work.SqlAlchemyUnitOfWork()
        , send_mail: Callable = email.send_mail
        , publish: Callable = redis_eventpublisher.publish
        , update_readmodel: Callable = redis_eventpublisher.update_readmodel
) -> messagebus.MessageBus:
    if start_orm:
        orm.start_mappers()

    dependencies = {
        'uow': uow
        , 'send_mail': send_mail
        , 'publish': publish
        , 'update_readmodel': update_readmodel
    }
    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies) for handler in event_handlers
        ] for event_type, event_handlers in handlers.EVENT_HANDLERS.items()
    }
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in handlers.COMMAND_HANDLERS.items()
    }

    return messagebus.MessageBus(
        uow=uow
        , event_handlers=injected_event_handlers
        , command_handlers=injected_command_handlers
    )
