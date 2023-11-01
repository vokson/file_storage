import os
import logging
from backend.adapters.file_storage.abstract import AbstractFileStorage
from backend.core import exceptions
from aiofiles import open as aopen
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

STORAGE_PATH = "/storage"
CHUNK_SIZE = 2**16


class LocalFileStorage(AbstractFileStorage):
    async def get(self, id: str)-> AsyncGenerator[bytes, None]:
        path = self._generate_path(id)

        if not os.path.isfile(path):
            raise exceptions.FileNotFound('File not found')

        # return open(self._generate_path(id), mode='rb')
        async with aopen(path, 'rb') as f:
            while True:
                chunk = await f.read(CHUNK_SIZE)

                if not chunk:
                    break

                yield chunk

    @staticmethod
    def _generate_path(id: str) -> str:
        return os.path.join(STORAGE_PATH, id[:2], id)
