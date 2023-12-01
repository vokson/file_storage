import logging
from uuid import UUID

from backend.core import exceptions
from backend.core.config import settings
from backend.domain.models import Account

from .abstract import AbstractAccountRepository

logger = logging.getLogger(__name__)


class DatabaseAccountRepository(AbstractAccountRepository):
    GET_ALL_QUERY = f"SELECT * FROM {settings.accounts_table};"

    GET_BY_NAME_QUERY = f"""
                    SELECT * FROM {settings.accounts_table}
                    WHERE name = $1;
                    """

    GET_BY_TOKEN_QUERY = f"""
                    SELECT * FROM {settings.accounts_table}
                    WHERE auth_token = $1;
                    """

    UPDATE_ACTUAL_SIZE_BY_NAME_QUERY = f"""
                    UPDATE {settings.accounts_table}
                    SET actual_size = $2 WHERE name = $1;
                    """

    UPDATE_ACTUAL_SIZE_BY_EXCLUDED_NAMES_QUERY = f"""
                    UPDATE {settings.accounts_table}
                    SET actual_size = $2 WHERE NOT ( name = ANY($1::text[]));
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

    async def get_all(self) -> list[Account]:
        logger.debug(f"Get all accounts")
        rows = await self._conn.fetch(self.GET_ALL_QUERY)
        return [self._convert_row_to_obj(x) for x in rows]

    async def get_by_token(self, auth_token: UUID) -> Account:
        logger.debug(f"Get account with token {auth_token}")
        return await self._get(self.GET_BY_TOKEN_QUERY, auth_token)

    async def update_actual_size(self, name: str, size: int):
        logger.debug(f"Set actual size {size} for account {name}")
        return await self._conn.execute(
            self.UPDATE_ACTUAL_SIZE_BY_NAME_QUERY, name, size
        )

    async def set_actual_size_for_excluded(
        self, excluded_names: list[str], size: int = 0
    ):
        logger.debug(
            f"Set actual size {size} for accounts where"
            f" name isn't included in {excluded_names}"
        )
        await self._conn.execute(
            self.UPDATE_ACTUAL_SIZE_BY_EXCLUDED_NAMES_QUERY,
            excluded_names,
            size,
        )

    async def verify_ready_to_add(self, account_name: str, tag: str) -> Account:
        logger.debug(f"Verify tag {tag} for account {account_name}")
        account_model: Account = await self.get_by_name(account_name)

        if not account_model.is_active:
            raise exceptions.AccountNotFound

        if tag not in account_model.tags:
            raise exceptions.TagNotFoundInAccount

        if account_model.actual_size >= account_model.total_size:
            raise exceptions.NoSpaceInAccount

        return account_model
        


async def get_db_account_repository(conn) -> AbstractAccountRepository:
    return DatabaseAccountRepository(conn)
