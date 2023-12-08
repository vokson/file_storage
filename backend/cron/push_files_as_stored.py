import asyncio
import logging
import os
import sys

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(BASE_DIR)

from backend.api.dependables import get_bus
from backend.cron.init import cleanup, startup
from backend.domain import commands, messages
from backend.service_layer.message_bus import MessageBus

logger = logging.getLogger()

CHUNK_SIZE = 1000


async def push(bus: MessageBus):
    offset = 0

    while True:
        cmd = commands.GetStoredAndNotDeletedFiles(CHUNK_SIZE, offset)
        files = await bus.handle(cmd)

        if not files:
            break

        for file in files:
            message = messages.FileStored(file)
            await bus.handle(commands.AddOutgoingBrokerMessage(message))

        logger.info(
            f"{len(files)} file with offset {offset} have been published"
        )

        offset += len(files)


async def main():
    await startup()

    bus = await get_bus()
    await push(bus)

    await cleanup()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
