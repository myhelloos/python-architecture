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
from tenacity import Retrying, stop_after_attempt, wait_exponential, RetryError

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


def handle_event(
        event: events.Event
        , queue: List[Message]
        , uow: unit_of_work.AbstractUnitOfWork
):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            for attempt in Retrying(
                    stop=stop_after_attempt(3)
                    , wait=wait_exponential()
            ):
                with attempt:
                    logger.debug('handling event %s with handler %s', event, handler)
                    handler(event, uow)
                    queue.extend(uow.collect_new_events())
        except RetryError as retry_failure:
            logger.exception(
                'Failed to handle event %s times, giving up'
                , retry_failure.last_attempt.attempt_number
            )
            continue


def handle_command(
        command: commands.Command
        , queue: List[Message]
        , uow: unit_of_work.AbstractUnitOfWork
):
    logger.debug('handling command %s', command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        handler(command, uow)
        queue.extend(uow.collect_new_events())
    except Exception:
        logger.exception('Exception handling cmmand %s', command)
        raise


def handle(
        message: Message
        , uow: unit_of_work.AbstractUnitOfWork
):
    queue = [message]

    while queue:
        message = queue.pop(0)

        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            handle_command(message, queue, uow)
        else:
            raise Exception(f'{message} was not an Event or Command')


EVENT_HANDLERS = {
    events.OutOfStock: [handlers.send_out_of_stock_notification]
    , events.Allocated: [
        handlers.publish_allocated_event
        , handlers.add_allocation_to_read_model
    ]
    , events.Deallocated: [
        handlers.remove_allocation_from_read_model
        , handlers.reallocate
    ]
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.CreateBatch: handlers.add_batch
    , commands.Allocate: handlers.allocate
    , commands.ChangeBatchQuantity: handlers.change_batch_quantity
}  # type: Dict[Type[commands.Command], Callable]
