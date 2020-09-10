#!/usr/bin/env python
# encoding: utf-8
# pylint: disable=broad-except, attribute-defined-outside-init
"""
@author: alfred
@license: (C) Copyright 2019-2020, Alfred Yuan Limited.
@time: 2020-09-06 23:01
@desc:
"""
from __future__ import annotations
import logging
from typing import Dict, Type, List, Callable, Union, TYPE_CHECKING

from allocation.domain import events, commands
from tenacity import Retrying, stop_after_attempt, wait_exponential, RetryError

if TYPE_CHECKING:
    from . import unit_of_work

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


class MessageBus:
    def __init__(
            self
            , uow: unit_of_work.AbstractUnitOfWork
            , event_handlers: Dict[Type[events.Event], List[Callable]]
            , command_handlers: Dict[Type[commands.Command, Callable]]
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    def handle(self, message: Message):
        self.queue = [message]

        while self.queue:
            message = self.queue.pop(0)

            if isinstance(message, events.Event):
                self.__handle_event(message)
            elif isinstance(message, commands.Command):
                self.__handle_command(message)
            else:
                raise Exception(f'{message} was not an Event or Command')

    def __handle_event(self, event: events.Event):
        for handler in self.event_handlers[type(event)]:
            try:
                for attempt in Retrying(
                        stop=stop_after_attempt(3)
                        , wait=wait_exponential()
                ):
                    with attempt:
                        logger.debug('handling event %s with handler %s', event, handler)
                        handler(event)
                        self.queue.extend(self.uow.collect_new_events())
            except RetryError as retry_failure:
                logger.exception(
                    'Failed to handle event %s times, giving up'
                    , retry_failure.last_attempt.attempt_number
                )
                continue

    def __handle_command(self, command: commands.Command):
        logger.debug('handling command %s', command)
        try:
            handler = self.command_handlers[type(command)]
            handler(command)
            self.queue.extend(self.uow.collect_new_events())
        except Exception:
            logger.exception('Exception handling cmmand %s', command)
            raise
