import logging
import os
import inspect
from pathlib import Path
from typing import AsyncGenerator, Awaitable, Callable
from collections.abc import AsyncIterator
from uuid import UUID

from aiofiles import open as aopen

from backend.adapters.file_storage.abstract import AbstractFileStorage
from backend.core import exceptions
from backend.core.config import settings

logger = logging.getLogger(__name__)

CHUNK_SIZE = 2**16


class LocalFileStorage(AbstractFileStorage):
    def __init__(self, path: str) -> None:
        self._storage_path = path

    def generate_path(self, id: UUID) -> str:
        return os.path.join(self._storage_path, str(id)[:2], str(id))

    async def get(self, id: UUID) -> AsyncGenerator[bytes, None]:
        path = self.generate_path(id)

        if not os.path.isfile(path):
            raise exceptions.FileNotFound

        async with aopen(path, "rb") as f:
            while True:
                chunk = await f.read(CHUNK_SIZE)

                if not chunk:
                    break

                yield chunk

    async def save(
        self,
        id: UUID,
        get_bytes: Callable[[int], Awaitable[bytearray]]
        | Callable[[int], AsyncIterator[bytes]],
    ) -> int:
        size = 0
        path = self.generate_path(id)
        print(f'PATH: {path}')
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)

        async with aopen(path, "wb") as f:
            if inspect.iscoroutinefunction(get_bytes):
                print('COROUTINE')
                while True:
                    chunk = await get_bytes(CHUNK_SIZE)

                    if not chunk:
                        break

                    size += len(chunk)
                    await f.write(chunk)

            else:
                print('ASYNC ITERATOR')
                async for chunk in get_bytes(CHUNK_SIZE):
                    size += len(chunk)
                    print('size', size)
                    await f.write(chunk)

        return size

    async def erase(
        self,
        id: UUID,
    ):
        path = self.generate_path(id)

        if not os.path.isfile(path):
            raise exceptions.FileNotFound

        Path(path).unlink(missing_ok=True)


async def get_local_file_storage() -> AbstractFileStorage:
    return LocalFileStorage(settings.storage_path)
