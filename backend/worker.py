import asyncio
import logging
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.api.dependables import get_bus
from backend.domain import commands
from backend.tools.worker import AbstractWorker

logger = logging.getLogger()


class Worker(AbstractWorker):
    async def _do(self):
        ok_ids = []
        future_publish_ids = []

        cmd = commands.GetMessagesReceivedFromBroker(self._chunk_size)
        messages = await self._bus.handle(cmd)

        if not messages:
            return

        self._delay_calculator.done()

        for message in messages:
            try:
                cmd = commands.ExecuteBrokerMessage(message)
                await self._bus.handle(cmd)
                is_ok = True

            except Exception as e:
                logger.error("Error during executing incoming message.")
                logger.info(e)
                is_ok = False

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


async def main():
    worker = Worker(await get_bus())

    await asyncio.gather(
        worker.run("Worker"),
    )


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
