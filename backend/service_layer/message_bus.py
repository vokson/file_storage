import logging
from sys import exc_info
from traceback import format_exception
from typing import Callable, Type

from backend.domain import commands, events
from backend.service_layer.handlers.command.dependables import COMMAND_HANDLERS
from backend.service_layer.handlers.event.dependables import EVENT_HANDLERS
from backend.service_layer.uow import AbstractUnitOfWork, UnitOfWork

# from django.core.exceptions import ValidationError
# from django.db import IntegrityError
# from django.db.models import ProtectedError


# from backend.core import  exceptions

# from .command_handlers import (
#     command_approval_handlers,
#     command_action_handlers,
#     command_action_type_handlers,
#     command_action_approval_handlers,
#     command_broker_handlers,
#     command_cart_handlers,
#     command_catalogue_handlers,
#     command_document_approval_handlers,
#     command_document_handlers,
#     command_file_handlers,
#     command_flow_handlers,
#     command_folder_handlers,
#     command_html_handlers,
#     command_load_item_handlers,
#     command_loader_handlers,
#     command_mail_handlers,
#     command_measure_handlers,
#     command_permission_handlers,
#     command_post_handlers,
#     command_project_handlers,
#     command_resource_handlers,
#     command_resource_item_handlers,
#     command_resource_list_group_handlers,
#     command_resource_list_handlers,
#     command_resource_list_item_handlers,
#     command_role_handlers,
#     command_service_handlers,
#     command_setting_handlers,
#     command_title_handlers,
#     command_transmittal_handlers,
#     command_user_folder_settings_handlers,
#     command_user_handlers,
#     command_user_search_schema_handlers,
# )
# from .event_handlers import (
#     event_action_handlers,
#     event_action_approval_handlers,
#     event_document_approval_handlers,
#     event_document_handlers,
#     event_document_post_handlers,
#     event_flow_handlers,
#     event_mail_handlers,
#     event_user_handlers,
# )

logger = logging.getLogger(__name__)


# class MessageBus:
#     def __init__(self, uow):
#         self._uow = uow

#     def handle(self, message):
#         queue = [message]
#         results = []

#         while queue:
#             message = queue.pop(0)
#             # print(message)

#             if isinstance(message, events.Event):
#                 self.handle_event(queue, message)

#             elif isinstance(message, commands.Command):
#                 results.append(self.handle_command(queue, message))

#             else:
#                 logger.exception(f"{message} was not an Event or Command")
#                 raise Exception(f"{message} was not an Event or Command")

#         # self._write_to_log(results)
#         return results

#     # def _write_to_log(self, results):
#     #     results.to_log()

#     def handle_event(self, queue, event):
#         for handler in EVENT_HANDLERS[type(event)]:
#             try:
#                 logger.debug("handling event %s with handler %s", event, handler)
#                 handler(event, self._uow, self.handle)
#                 queue.extend(self._uow.collect_new_messages())
#             except Exception as e:
#                 logger.exception(f"Exception {e} handling event %s", event)
#                 continue

#     def handle_command(self, queue, command):
#         logger.debug("handling command %s", command)

#         try:
#             handler = COMMAND_HANDLERS[type(command)]
#             result = handler(command, self._uow, self.handle)
#             queue.extend(self._uow.collect_new_messages())
#             return result

#         except Exception as e:
#             logger.exception(f"Exception {e} handling command %s", command)
#             raise e

#     # def _handle_exception(self, error):
#     #     cls = RESULTS.get(error.__class__)

#     #     if cls:
#     #         return cls(str(error))


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

    # def _handle_exception(self, error):
    #     cls = RESULTS.get(error.__class__)

    #     if not cls:
    #         for parent_class in RESULTS.keys():
    #             if isinstance(error, parent_class):
    #                 cls = RESULTS[parent_class]
    #                 break

    #     if cls:
    #         return cls(str(error))


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
