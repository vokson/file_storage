import logging
from abc import ABC, abstractmethod
from backend.domain.models import Link
from uuid import UUID

logger = logging.getLogger(__name__)


class AbstractLinkRepository(ABC):
    DOWNLOAD_LINK_TYPE = 'D'

    def _convert_row_to_obj(self, row) -> Link:
        return Link(**dict(row.items()))

    @abstractmethod
    async def add(self, model: Link):
        pass
