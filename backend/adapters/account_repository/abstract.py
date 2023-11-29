import logging
from abc import ABC, abstractmethod
from uuid import UUID

from backend.domain.models import Account

logger = logging.getLogger(__name__)


class AbstractAccountRepository(ABC):
    def _convert_row_to_obj(self, row) -> Account:
        return Account(**dict(row.items()))

    @abstractmethod
    async def get_by_name(self, name: str) -> Account:
        pass

    @abstractmethod
    async def get_by_token(self, auth_token: UUID) -> Account:
        pass
