import logging
from abc import ABC, abstractmethod
from uuid import UUID

from backend.domain.models import Account

logger = logging.getLogger(__name__)


class AbstractAccountRepository(ABC):
    def _convert_row_to_obj(self, row) -> Account:
        return Account(**dict(row.items()))

    @abstractmethod
    async def get_all(self) -> list[Account]:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Account:
        pass

    @abstractmethod
    async def get_by_token(self, auth_token: UUID) -> Account:
        pass

    @abstractmethod
    async def update_actual_size(self, name: str, size: int):
        pass

    @abstractmethod
    async def set_actual_size_for_excluded(
        self, excluded_names: list[str], size: int = 0
    ):
        pass
