import asyncio
import logging
import os
import sys

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(BASE_DIR)

from backend.api.dependables import get_bus
from backend.domain import commands
from backend.service_layer.message_bus import MessageBus

from backend.cron.init import cleanup, startup

logger = logging.getLogger()


async def do(bus: MessageBus):
    cmd = commands.UpdateAccountsActualSizes()
    await bus.handle(cmd)


async def main():
    await startup()

    bus = await get_bus()
    await do(bus)

    await cleanup()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
