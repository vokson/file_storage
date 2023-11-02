import logging
from abc import ABC, abstractmethod
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


class AbstractFileStorage(ABC):
    @abstractmethod
    async def get(self, id: str) -> AsyncGenerator[bytes, None]:
        pass

