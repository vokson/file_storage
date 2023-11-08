import logging

import pytest_asyncio

from backend.adapters.file_storage.local import LocalFileStorage

logger = logging.Logger(__name__)


@pytest_asyncio.fixture()
async def file_storage(tmp_path):
    storage = LocalFileStorage(tmp_path.name)
    yield storage
