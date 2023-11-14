import logging
from abc import ABC, abstractmethod
from uuid import UUID

from backend.domain.models import BrokerMessage

logger = logging.getLogger(__name__)


class AbstractBrokerMessageRepository(ABC):
    OUT_DIRECTION = "O"
    IN_DIRECTION = "I"

    def __init__(self, conn):
        self._conn = conn

    def _convert_row_to_obj(self, row) -> BrokerMessage:
        return BrokerMessage(**dict(row.items()))

    @abstractmethod
    async def get_by_id(self, id: UUID) -> BrokerMessage:
        pass

    @abstractmethod
    async def get_not_executed_outgoing(
        self, chunk_size: int
    ) -> list[BrokerMessage]:
        pass

    @abstractmethod
    async def get_not_executed_incoming(
        self, chunk_size: int
    ) -> list[BrokerMessage]:
        pass

    @abstractmethod
    async def add_outgoing(
        self, key: str, body: dict, delay_in_seconds: int = 0
    ) -> BrokerMessage:
        pass

    @abstractmethod
    async def add_incoming(
        self, app: str, key: str, body: dict, delay_in_seconds: int = 0
    ) -> BrokerMessage:
        pass

    @abstractmethod
    async def mark_as_executed(self, ids: list[UUID]):
        pass

    @abstractmethod
    async def schedule_next_retry(self, ids: list[UUID]):
        pass
