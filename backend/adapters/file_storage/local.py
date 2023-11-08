import logging
import os
from pathlib import Path
from typing import AsyncGenerator, Awaitable, Callable
from uuid import UUID

from aiofiles import open as aopen

from backend.adapters.file_storage.abstract import AbstractFileStorage
from backend.core import exceptions
from backend.core.config import settings

logger = logging.getLogger(__name__)

CHUNK_SIZE = 2**16


class LocalFileStorage(AbstractFileStorage):
    async def get(self, id: UUID)-> AsyncGenerator[bytes, None]:
        path = self._generate_path(id)

        if not os.path.isfile(path):
            raise exceptions.FileNotFound

        async with aopen(path, 'rb') as f:
            while True:
                chunk = await f.read(CHUNK_SIZE)

                if not chunk:
                    break

                yield chunk

    @staticmethod
    def _generate_path(id: UUID) -> str:
        return os.path.join(settings.storage_path, str(id)[:2], str(id))

    async def save(
        self,
        id: UUID,
        get_coro_with_bytes_func: Callable[[int], Awaitable[bytearray]]
    ) -> int:
        size = 0
        path = self._generate_path(id)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)

        async with aopen(path, 'wb') as f:
            while True:
                chunk = await get_coro_with_bytes_func(CHUNK_SIZE)

                if not chunk:
                    break

                size += len(chunk)
                await f.write(chunk)

        return size

    async def erase(
        self,
        id: UUID,
    ):
        path = self._generate_path(id)

        if not os.path.isfile(path):
            raise exceptions.FileNotFound

        Path(path).unlink(missing_ok=True)

async def get_local_file_storage() -> AbstractFileStorage:
    return LocalFileStorage()
