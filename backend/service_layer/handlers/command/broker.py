import logging

from backend.core.config import settings
from backend.domain import commands, models
from backend.service_layer.uow import AbstractUnitOfWork

logger = logging.getLogger(__name__)


async def get_not_executed_outgoing(
    cmd: commands.GetMessagesToBeSendToBroker,
    uow: AbstractUnitOfWork,
) -> list[models.BrokerMessage]:
    async with uow:
        return await uow.broker_message_repository.get_not_executed_outgoing(
            cmd.chunk_size
        )


async def get_not_executed_incoming(
    cmd: commands.GetMessagesReceivedFromBroker,
    uow: AbstractUnitOfWork,
) -> list[models.BrokerMessage]:
    async with uow:
        return await uow.broker_message_repository.get_not_executed_incoming(
            cmd.chunk_size
        )


async def add_outgoing(
    cmd: commands.AddOutgoingBrokerMessage,
    uow: AbstractUnitOfWork,
) -> None:
    async with uow:
        await uow.broker_message_repository.add_outgoing(
            cmd.message.key, cmd.message.to_broker, cmd.delay
        )
        await uow.commit()


async def add_incoming(
    cmd: commands.AddIncomingBrokerMessage,
    uow: AbstractUnitOfWork,
) -> None:
    async with uow:
        await uow.broker_message_repository.add_incoming(
            cmd.id, cmd.app, cmd.key, cmd.body
        )
        await uow.commit()


async def mark_as_executed(
    cmd: commands.MarkBrokerMessageAsExecuted,
    uow: AbstractUnitOfWork,
):
    async with uow:
        await uow.broker_message_repository.mark_as_executed(cmd.ids)
        await uow.commit()


async def schedule_next_retry(
    cmd: commands.ScheduleNextRetryForBrokerMessage,
    uow: AbstractUnitOfWork,
):
    async with uow:
        await uow.broker_message_repository.schedule_next_retry(cmd.ids)
        await uow.commit()


async def publish(
    cmd: commands.PublishMessageToBroker,
    uow: AbstractUnitOfWork,
) -> bool:
    return await uow.broker_publisher.push_message(
        cmd.message.app, cmd.message.key, cmd.message.body, cmd.message.id
    )


async def execute(
    cmd: commands.ExecuteBrokerMessage,
    uow: AbstractUnitOfWork,
):
    handlers = {
        settings.app_name: {
            "FILE.DELETED": file_deleted_handler,
            "FILE.STORED": file_stored_handler,
        }
    }

    if cmd.message.app not in handlers:
        return

    handler = handlers[cmd.message.app].get(cmd.message.key)

    if not handler:
        return

    await handler(uow, cmd.message.body)


async def file_deleted_handler(uow: AbstractUnitOfWork, data: dict):
    logger.debug("File deleted broker message handler")
    uow.push_message(commands.DeleteFile(data["account_id"], data["id"]))


async def file_stored_handler(uow: AbstractUnitOfWork, data: dict):
    logger.debug("File stored broker message handler")
    uow.push_message(
        commands.CloneFile(
            data["account_id"], data["id"], data["name"], data["size"]
        )
    )


async def delete_executed(
    cmd: commands.DeleteExecutedBrokerMessages,
    uow: AbstractUnitOfWork,
):
    async with uow:
        await uow.broker_message_repository.delete_executed()
        await uow.commit()