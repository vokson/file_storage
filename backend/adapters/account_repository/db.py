import logging
from .abstract import AbstractAccountRepository
from backend.domain.models import Account
from uuid import UUID
from typing import AsyncGenerator, Coroutine
from backend.core.config import settings
from backend.core import exceptions

logger = logging.getLogger(__name__)


class DatabaseAccountRepository(AbstractAccountRepository):
    GET_BY_TOKEN_QUERY = f"""
                    SELECT * FROM {settings.accounts_table}
                    WHERE auth_token = $1;
                    """

    def __init__(self, conn):
        self._conn = conn

    async def get_by_token(self, auth_token: UUID) -> Account:
        logger.debug(f"Get account with token {auth_token}")
        row = await self._conn.fetchrow(self.GET_BY_TOKEN_QUERY, auth_token)
        if not row:
            raise exceptions.AccountNotFound

        return self._convert_row_to_obj(row)


async def get_db_account_repository(conn) -> AbstractAccountRepository:
    return DatabaseAccountRepository(conn)
