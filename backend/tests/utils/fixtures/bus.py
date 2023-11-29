import logging

import aiohttp
import pytest_asyncio

logger = logging.Logger(__name__)


@pytest_asyncio.fixture()
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()
