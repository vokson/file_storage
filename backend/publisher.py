import asyncio
import sys
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.service_layer.message_bus import get_message_bus
from backend.tools.delay import DelayCalculator
from backend.domain import commands

logger = logging.getLogger()


async def get_bus():
    return await get_message_bus(
        [
            "broker_publisher",
            "db",
            "broker_message_repository",
        ]
    )


class MessageCollector:
    def __init__(
        self,
        bus,
        delay_calculator=DelayCalculator(limit=5),
        chunk_size=1000,
    ):
        self._bus = bus
        self._delay_calculator = delay_calculator
        self._chunk_size = chunk_size

    async def run(self):
        while True:
            try:
                await self._do()
            except Exception as e:
                logger.error("Error in MessageCollector during running")
                logger.info(e)

            sleep_time = self._delay_calculator.get()
            logger.info(f"Sleeping {sleep_time} seconds.")
            await asyncio.sleep(sleep_time)

    async def _do(self):
        ok_ids = []
        future_publish_ids = []

        cmd = commands.GetMessagesToBeSendToBroker(self._chunk_size)
        messages = await self._bus.handle(cmd)

        if not messages:
            return

        self._delay_calculator.done()

        for message in messages:
            cmd = commands.PublishMessageToBroker(
                message.id,
                message.app,
                message.key,
                message.body,
            )
            is_ok = await self._bus.handle(cmd)

            if is_ok:
                logger.info(f"Send {message.id} - OK.")
                ok_ids.append(message.id)
                continue

            logger.warning(f"Send {message.id} - RESCHEDULED.")
            future_publish_ids.append(message.id)

        cmd = commands.MarkBrokerMessageAsExecuted(ok_ids)
        messages = await self._bus.handle(cmd)

        cmd = commands.ScheduleNextRetryForBrokerMessage(future_publish_ids)
        messages = await self._bus.handle(cmd)


async def main():
    message_collector = MessageCollector(
        await get_bus()
    )

    await asyncio.gather(
        message_collector.run(),
    )


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
