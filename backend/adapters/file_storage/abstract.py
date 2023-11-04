import logging
from uuid import UUID
from abc import ABC, abstractmethod
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


class AbstractFileStorage(ABC):
    @abstractmethod
    async def get(self, id: UUID) -> AsyncGenerator[bytes, None]:
        pass

