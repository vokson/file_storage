from collections import OrderedDict
from uuid import UUID, uuid4
from datetime import datetime

from backend.core.config import settings, tz_now
from backend.domain.models import BaseModel

class CommonMixin:
    @classmethod
    def _cmp(cls, a: OrderedDict, b: BaseModel):
        for key in a:
            assert a[key] == getattr(b, key)

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
    ) -> UUID:
        await conn.execute(
            cls.ACCOUNT_ADD_QUERY, id, name, auth_token, is_active
        )
        return id

    @classmethod
    async def _create_default_account(cls, conn) -> UUID:
        return await cls._create_account(
            conn, *cls.DEFAULT_ACCOUNT_PARAMETERS.values()
        )


class FileMixin:
    DEFAULT_FILE_PARAMETERS = OrderedDict(
        [
            ("id", uuid4()),
            ("stored_id", uuid4()),
            ("name", "FILENAME"),
            ("size", 100),
            ("created", tz_now()),
            ("has_stored", True),
            ("stored", tz_now()),
            ("has_deleted", False),
            ("deleted", None),
            ("has_erased", False),
            ("erased", None),
        ]
    )

    DEFAULT_NOT_STORED_FILE_PARAMETERS = OrderedDict(
        [
            ("id", uuid4()),
            ("stored_id", uuid4()),
            ("name", "FILENAME"),
            ("size", 100),
            ("created", tz_now()),
            ("has_stored", False),
            ("stored", None),
            ("has_deleted", False),
            ("deleted", None),
            ("has_erased", False),
            ("erased", None),
        ]
    )

    DEFAULT_DELETED_FILE_PARAMETERS = OrderedDict(
        [
            ("id", uuid4()),
            ("stored_id", uuid4()),
            ("name", "FILENAME"),
            ("size", 100),
            ("created", tz_now()),
            ("has_stored", True),
            ("stored", tz_now()),
            ("has_deleted", True),
            ("deleted", tz_now()),
            ("has_erased", False),
            ("erased", None),
        ]
    )

    FILE_ADD_QUERY = f"""
                    INSERT INTO {settings.files_table}
                        (
                            id,
                            stored_id,
                            name,
                            size,
                            created,
                            has_stored,
                            stored,
                            has_deleted,
                            deleted,
                            has_erased,
                            erased,
                            account_id
                        )
                    VALUES
                        ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12);
                    """

    @classmethod
    async def _create_file(
        cls,
        conn,
        id: UUID,
        stored_id: UUID,
        name: str,
        size: int,
        created: datetime,
        has_stored: bool,
        stored: datetime | None,
        has_deleted: bool,
        deleted: datetime | None,
        has_erased: bool,
        erased: datetime | None,
        account_id: UUID,
    ) -> UUID:
        await conn.execute(
            cls.FILE_ADD_QUERY,
            id,
            stored_id,
            name,
            size,
            created,
            has_stored,
            stored,
            has_deleted,
            deleted,
            has_erased,
            erased,
            account_id,
        )
        return id

    @classmethod
    async def _create_default_file(cls, conn, account_id) -> UUID:
        return await cls._create_file(
            conn, *cls.DEFAULT_FILE_PARAMETERS.values(), account_id
        )

    @classmethod
    async def _create_default_not_stored_file(cls, conn, account_id) -> UUID:
        return await cls._create_file(
            conn, *cls.DEFAULT_NOT_STORED_FILE_PARAMETERS.values(), account_id
        )

    @classmethod
    async def _create_default_deleted_file(cls, conn, account_id) -> UUID:
        return await cls._create_file(
            conn, *cls.DEFAULT_DELETED_FILE_PARAMETERS.values(), account_id
        )
