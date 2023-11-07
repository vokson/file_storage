import logging
from abc import ABC, abstractmethod
from backend.domain.models import Link
from uuid import UUID

logger = logging.getLogger(__name__)


class AbstractLinkRepository(ABC):
    DOWNLOAD_LINK_TYPE = "D"
    UPLOAD_LINK_TYPE = "U"

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
        self, link_id: UUID, file_id: UUID, expire_period_in_sec: int
    ) -> Link:
        pass

    @abstractmethod
    async def add_upload(
        self, link_id: UUID, file_id: UUID, expire_period_in_sec: int
    ) -> Link:
        pass

    @abstractmethod
    async def delete(self, link_id: UUID):
        pass

    @abstractmethod
    async def delete_by_file_id(self, file_id: UUID):
        pass
