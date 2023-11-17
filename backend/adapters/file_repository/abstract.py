import logging
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Awaitable, Callable, Coroutine
from uuid import UUID

from backend.adapters.file_storage.abstract import AbstractFileStorage
from backend.domain.models import File

logger = logging.getLogger(__name__)


class AbstractFileRepository(ABC):
    def __init__(self, storage: AbstractFileStorage):
        self._storage = storage

    def _convert_row_to_obj(self, row) -> File:
        return File(**dict(row.items()))

    @abstractmethod
    async def get(self, id: UUID) -> File:
        pass

    @abstractmethod
    async def get_not_stored(self, id: UUID) -> File:
        pass

    @abstractmethod
    async def add(self, account_id: UUID, file_id: UUID | None = None) -> File:
        pass

    @abstractmethod
    async def take(
        self, file_id: UUID
    ) -> Coroutine[None, None, AsyncGenerator[bytes, None]]:
        pass

    @abstractmethod
    async def store(
        self,
        file_id: UUID,
        get_coro_with_bytes_func: Callable[[int], Awaitable[bytearray]],
    ) -> int:
        pass

    @abstractmethod
    async def mark_as_stored(self, file_id: UUID, name: str, size: int) -> File:
        pass

    @abstractmethod
    async def delete(self, account_id: UUID, file_id: UUID) -> File:
        pass

    @abstractmethod
    async def erase(self, file_id: UUID):
        pass
