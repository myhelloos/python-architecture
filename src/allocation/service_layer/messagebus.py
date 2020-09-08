#!/usr/bin/env python
# encoding: utf-8
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020-09-06 23:01
@desc:
"""
import logging
from typing import Dict, Type, List, Callable, Union

from allocation.domain import events, commands
from allocation.service_layer import unit_of_work, handlers

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


def handle_event(
        event: events.Event
        , queue: List[Message]
        , uow: unit_of_work.AbstractUnitOfWork
):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            logger.debug('handling event %s with handler %s', event, handler)
            handler(event, uow)
            queue.extend(uow.collect_new_events())
        except Exception:
            logger.exception('Exception handling event %s', event)
            continue


def handle_command(
        command: commands.Command
        , queue: List[Message]
        , uow: unit_of_work.AbstractUnitOfWork
):
    logger.debug('handling command %s', command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception('Exception handling cmmand %s', command)
        raise


def handle(
        message: Message
        , uow: unit_of_work.AbstractUnitOfWork
):
    queue = [message]

    results = []
    while queue:
        message = queue.pop(0)

        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f'{message} was not an Event or Command')

    return results


EVENT_HANDLERS = {
    events.OutOfStock: [handlers.send_out_of_stock_notification]
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.CreateBatch: handlers.add_batch
    , commands.Allocate: handlers.allocate
    , commands.ChangeBatchQuantity: handlers.change_batch_qunatity
}  # type: Dict[Type[commands.Command], Callable]
