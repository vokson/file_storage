import logging
from abc import ABC, abstractmethod
from typing import AsyncGenerator
from uuid import UUID

logger = logging.getLogger(__name__)


class AbstractFileStorage(ABC):
    @abstractmethod
    async def get(self, id: UUID) -> AsyncGenerator[bytes, None]:
        pass

    @abstractmethod
    async def save(
        self,
        id: UUID,
        bytes_gen: AsyncGenerator[bytes, None],
    ) -> int:
        pass

    @abstractmethod
    async def erase(
        self,
        id: UUID,
    ) -> bool:
        pass
