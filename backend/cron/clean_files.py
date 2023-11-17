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
from backend.core.config import settings

logger = logging.getLogger()


async def main():
    bus = await get_bus()
    cmd = commands.EraseDeletedFiles(settings.storage_time_for_files)
    await bus.handle(cmd)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
