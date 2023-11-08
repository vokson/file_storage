from collections import OrderedDict
from uuid import UUID, uuid4

from backend.core.config import settings


class AccountMixin:
    DEFAULT_ACCOUNT_PARAMETERS = OrderedDict(
            [
                ("id", uuid4()),
                ("name", "TEST ACCOUNT"),
                ("auth_token", uuid4()),
                ("is_active", True),
            ]
        )

    ACCOUNT_ADD_QUERY = f"""
                    INSERT INTO {settings.accounts_table}
                        (
                            id,
                            name,
                            auth_token,
                            is_active
                        )
                    VALUES
                        ($1, $2, $3, $4);
                    """

    @classmethod
    async def _create_account(
        cls, conn, id: UUID, name: str, auth_token: UUID, is_active: bool
    ):
        await conn.execute(
            cls.ACCOUNT_ADD_QUERY, id, name, auth_token, is_active
        )

    @classmethod
    async def _create_default_account(cls, conn):
        await cls._create_account(
            conn, *cls.DEFAULT_ACCOUNT_PARAMETERS.values()
        )
