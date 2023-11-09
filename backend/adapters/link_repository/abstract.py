import logging
from abc import ABC, abstractmethod
from uuid import UUID

from backend.domain.models import Link

logger = logging.getLogger(__name__)


class AbstractLinkRepository(ABC):
    DOWNLOAD_LINK_TYPE = "D"
    UPLOAD_LINK_TYPE = "U"

    def __init__(self, conn):
        self._conn = conn

    def _convert_row_to_obj(self, row) -> Link:
        return Link(**dict(row.items()))

    @abstractmethod
    async def get_download(self, id: UUID) -> Link:
        pass

    @abstractmethod
    async def get_upload(self, id: UUID) -> Link:
        pass

    @abstractmethod
    async def add_download(
        self, file_id: UUID, expire_period_in_sec: int
    ) -> Link:
        pass

    @abstractmethod
    async def add_upload(
        self, file_id: UUID, expire_period_in_sec: int
    ) -> Link:
        pass

    @abstractmethod
    async def delete(self, link_id: UUID):
        pass

    @abstractmethod
    async def delete_by_file_id(self, file_id: UUID):
        pass
