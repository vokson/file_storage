import logging

from backend.domain import commands, events, messages
from backend.service_layer.uow import AbstractUnitOfWork

logger = logging.getLogger(__name__)


async def deleted(
    evt: events.FileDeleted,
    uow: AbstractUnitOfWork,
):
    message = messages.FileDeleted(evt.file)
    cmd = commands.AddOutgoingBrokerMessage(message)
    uow.push_message(cmd)


async def stored(
    evt: events.FileStored,
    uow: AbstractUnitOfWork,
):
    message = messages.FileStored(evt.file)
    cmd = commands.AddOutgoingBrokerMessage(message)
    uow.push_message(cmd)