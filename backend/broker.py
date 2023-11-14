import asyncio
import logging
import os
import sys
from uuid import UUID

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.adapters.broker import RabbitConsumer
from backend.core.config import broker_url, settings
from backend.domain import commands
from backend.service_layer.message_bus import get_message_bus
from backend.tools.worker import AbstractWorker

logger = logging.getLogger()


class MessagePublisher(AbstractWorker):
    async def _do(self):
        ok_ids = []
        future_publish_ids = []

        cmd = commands.GetMessagesToBeSendToBroker(self._chunk_size)
        messages = await self._bus.handle(cmd)

        if not messages:
            return

        self._delay_calculator.done()

        for message in messages:
            cmd = commands.PublishMessageToBroker(message)
            is_ok = await self._bus.handle(cmd)

            if is_ok:
                logger.info(f"Send {message.id} - OK.")
                ok_ids.append(message.id)
                continue

            logger.warning(f"Send {message.id} - RESCHEDULED.")
            future_publish_ids.append(message.id)

        if ok_ids:
            cmd = commands.MarkBrokerMessageAsExecuted(ok_ids)
            messages = await self._bus.handle(cmd)

        if future_publish_ids:
            cmd = commands.ScheduleNextRetryForBrokerMessage(
                future_publish_ids
            )
            messages = await self._bus.handle(cmd)


def handler_for_new_broker_message(bus):
    async def inner(
        message_id: str, app_id: str, routing_key: str, body: dict
    ) -> bool:
        try:
            cmd = commands.AddIncomingBrokerMessage(
                UUID(message_id), app_id, routing_key, body
            )
            await bus.handle(cmd)
            return True

        except Exception as e:
            logger.error("Error during saving incoming message.")
            logger.info(e)
            return False

    return inner


async def main():
    message_publisher = MessagePublisher(
        await get_message_bus(
            [
                "broker_publisher",
                "db",
                "broker_message_repository",
            ]
        )
    )
    message_consumer = RabbitConsumer(
        broker_url,
        settings.broker.exchange,
        settings.broker.queue,
        handler_for_new_broker_message(
            await get_message_bus(
                [
                    "db",
                    "broker_message_repository",
                ]
            )
        ),
    )

    await asyncio.gather(
        message_publisher.run("MessagePublisher"),
        message_consumer.run(),
    )


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
