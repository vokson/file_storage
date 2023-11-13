import logging

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
    return await uow.broker_publisher.push_message(cmd.app, cmd.key, cmd.body, cmd.id)
