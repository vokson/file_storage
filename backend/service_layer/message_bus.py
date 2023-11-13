import logging
from sys import exc_info
from traceback import format_exception
from typing import Callable, Type

from backend.domain import commands, events
from backend.service_layer.handlers.command.dependables import COMMAND_HANDLERS
from backend.service_layer.handlers.event.dependables import EVENT_HANDLERS
from backend.service_layer.uow import AbstractUnitOfWork, UnitOfWork

logger = logging.getLogger(__name__)


def print_exception():
    etype, value, tb = exc_info()
    info, error = format_exception(etype, value, tb)[-2:]
    logger.info(f"EXCEPTION IN:\n{info}\n{error}")


class MessageBus:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        event_handlers: dict[Type[events.Event], list[Callable]],
        command_handlers: dict[Type[commands.Command], Callable],
    ):
        self._uow = uow
        self._event_handlers = event_handlers
        self._command_handlers = command_handlers

    async def handle(self, message: commands.Command | events.Event):
        queue = [message]
        results = []

        while queue:
            logger.debug(f'QUEUE: {queue}')
            message = queue.pop(0)

            if isinstance(message, events.Event):
                await self._handle_event(message)
                queue.extend(self._uow.collect_new_messages())

            elif isinstance(message, commands.Command):
                results.append(await self._handle_command(message))
                queue.extend(self._uow.collect_new_messages())

            else:
                raise Exception(f"{message} was not an Event or Command")

        return results[0]

    async def _handle_event(self, event: events.Event):
        for handler in self._event_handlers[type(event)]:
            try:
                logger.debug(f"Handling event {event} with handler {handler}")
                await handler(event, self._uow)

            except Exception:
                print_exception()
                logger.error(f"Exception handling event {event}")
                continue

    async def _handle_command(self, command: commands.Command):
        logger.debug(f"Handling command {command}")

        try:
            handler = self._command_handlers[type(command)]
            return await handler(command, self._uow)

        except Exception as e:
            print_exception()
            logger.error(f"Exception handling command {command}")
            raise e


async def get_message_bus(
    bootstrap: list[str],
    uow: AbstractUnitOfWork | None = None,
    event_handlers: dict[
        Type[events.Event],
        list[Callable],
    ] = EVENT_HANDLERS,
    command_handlers: dict[
        Type[commands.Command],
        Callable
    ] = COMMAND_HANDLERS,
):
    if not uow:
        uow = UnitOfWork(bootstrap)
        await uow.startup()

    bus = MessageBus(uow, event_handlers, command_handlers)
    return bus
