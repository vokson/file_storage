import logging
from abc import ABC, abstractmethod
from backend.domain.models import File
from backend.adapters.file_storage.abstract import AbstractFileStorage
from uuid import UUID

logger = logging.getLogger(__name__)


class AbstractFileRepository(ABC):
    def __init__(self, storage: AbstractFileStorage):
        self._storage = storage

    def _convert_row_to_obj(self, row) -> File:
        return File(**dict(row.items()))

    @abstractmethod
    async def get(self, id: UUID) -> File:
        pass
