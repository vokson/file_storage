import logging
import os
from typing import AsyncGenerator

from aiofiles import open as aopen
from pydantic import UUID4

from backend.adapters.file_storage.abstract import AbstractFileStorage
from backend.core import exceptions
from backend.core.config import settings

logger = logging.getLogger(__name__)

CHUNK_SIZE = 2**16


class LocalFileStorage(AbstractFileStorage):
    async def get(self, id: UUID4)-> AsyncGenerator[bytes, None]:
        path = self._generate_path(id)

        if not os.path.isfile(path):
            raise exceptions.FileNotFound('File not found')

        async with aopen(path, 'rb') as f:
            while True:
                chunk = await f.read(CHUNK_SIZE)

                if not chunk:
                    break

                yield chunk

    @staticmethod
    def _generate_path(id: UUID4) -> str:
        return os.path.join(settings.storage_path, str(id)[:2], str(id))


async def get_local_file_storage() -> AbstractFileStorage:
    return LocalFileStorage()
