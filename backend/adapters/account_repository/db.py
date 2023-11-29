import logging
from uuid import UUID

from backend.core import exceptions
from backend.core.config import settings
from backend.domain.models import Account

from .abstract import AbstractAccountRepository

logger = logging.getLogger(__name__)


class DatabaseAccountRepository(AbstractAccountRepository):
    GET_BY_NAME_QUERY = f"""
                    SELECT * FROM {settings.accounts_table}
                    WHERE name = $1;
                    """

    GET_BY_TOKEN_QUERY = f"""
                    SELECT * FROM {settings.accounts_table}
                    WHERE auth_token = $1;
                    """

    def __init__(self, conn):
        self._conn = conn

    async def _get(self, query: str, *args) -> Account:
        row = await self._conn.fetchrow(query, *args)
        if not row:
            raise exceptions.AccountNotFound

        return self._convert_row_to_obj(row)

    async def get_by_name(self, name: str) -> Account:
        logger.debug(f"Get account with name {name}")
        return await self._get(self.GET_BY_NAME_QUERY, name)

    async def get_by_token(self, auth_token: UUID) -> Account:
        logger.debug(f"Get account with token {auth_token}")
        return await self._get(self.GET_BY_TOKEN_QUERY, auth_token)


async def get_db_account_repository(conn) -> AbstractAccountRepository:
    return DatabaseAccountRepository(conn)
