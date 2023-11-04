import logging
from abc import ABC, abstractmethod
from backend.domain.models import Account
from uuid import UUID

logger = logging.getLogger(__name__)


class AbstractAccountRepository(ABC):
    def _convert_row_to_obj(self, row) -> Account:
        return Account(**dict(row.items()))

    @abstractmethod
    async def get_by_token(self, auth_token: UUID) -> Account:
        pass
