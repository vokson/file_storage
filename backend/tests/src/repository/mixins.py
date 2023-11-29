from collections import OrderedDict
from datetime import datetime
from uuid import UUID, uuid4

from backend.core.config import settings, tz_now
from backend.domain.models import BaseModel


class CommonMixin:
    @classmethod
    def _cmp(cls, a: OrderedDict, b: BaseModel):
        for key in a:
            x = a[key]
            y = getattr(b, key)

            if type(x) is datetime:
                x = int(x.timestamp())

            if type(y) is datetime:
                y = int(y.timestamp())


class AccountMixin:
    DEFAULT_ACCOUNT_PARAMETERS = OrderedDict(
        [
            ("name", "TEST ACCOUNT"),
            ("auth_token", uuid4()),
            ("is_active", True),
        ]
    )

    ACCOUNT_ADD_QUERY = f"""
                    INSERT INTO {settings.accounts_table}
                        (
                            name,
                            auth_token,
                            is_active
                        )
                    VALUES
                        ($1, $2, $3);
                    """

    @classmethod
    async def _create_account(
        cls, conn, name: str, auth_token: UUID, is_active: bool
    ) -> tuple[UUID, UUID]:
        await conn.execute(cls.ACCOUNT_ADD_QUERY, name, auth_token, is_active)
        return name, auth_token

    @classmethod
    async def _create_default_account(cls, conn) -> tuple[UUID, UUID]:
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
                account_name
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
        account_name: str,
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
            account_name,
        )
        return id

    @classmethod
    async def _create_default_file(cls, conn, account_name) -> UUID:
        return await cls._create_file(
            conn, *cls.DEFAULT_FILE_PARAMETERS.values(), account_name
        )

    @classmethod
    async def _create_default_not_stored_file(cls, conn, account_name) -> UUID:
        return await cls._create_file(
            conn,
            *cls.DEFAULT_NOT_STORED_FILE_PARAMETERS.values(),
            account_name,
        )

    @classmethod
    async def _create_default_deleted_file(cls, conn, account_name) -> UUID:
        return await cls._create_file(
            conn, *cls.DEFAULT_DELETED_FILE_PARAMETERS.values(), account_name
        )


class LinkMixin:
    DEFAULT_DOWNLOAD_LINK_PARAMETERS = OrderedDict(
        [
            ("id", uuid4()),
            ("type", "D"),
            ("created", tz_now()),
            ("expired", tz_now(settings.storage_time_for_links)),
        ]
    )

    DEFAULT_UPLOAD_LINK_PARAMETERS = OrderedDict(
        [
            ("id", uuid4()),
            ("type", "U"),
            ("created", tz_now()),
            ("expired", tz_now(settings.storage_time_for_links)),
        ]
    )

    LINK_ADD_QUERY = f"""
                    INSERT INTO {settings.links_table}
                        (
                            id,
                            type,
                            created,
                            expired,
                            file_id
                        )
                    VALUES
                        ($1, $2, $3, $4, $5);
                    """

    @classmethod
    async def _create_link(
        cls,
        conn,
        id: UUID,
        type: str,
        created: datetime,
        expired: datetime,
        file_id: UUID,
    ) -> UUID:
        await conn.execute(
            cls.LINK_ADD_QUERY, id, type, created, expired, file_id
        )
        return id

    @classmethod
    async def _create_default_download_link(cls, conn, file_id: UUID) -> UUID:
        return await cls._create_link(
            conn, *cls.DEFAULT_DOWNLOAD_LINK_PARAMETERS.values(), file_id
        )

    @classmethod
    async def _create_default_upload_link(cls, conn, file_id: UUID) -> UUID:
        return await cls._create_link(
            conn, *cls.DEFAULT_UPLOAD_LINK_PARAMETERS.values(), file_id
        )


class BrokerMessageMixin:
    DEFAULT_OUT_BROKER_MESSAGE_PARAMETERS = OrderedDict(
        [
            ("id", uuid4()),
            ("direction", "O"),
            ("app", "APP"),
            ("key", "KEY"),
            ("body", {"key": "value"}),
            ("has_executed", False),
            ("created", tz_now()),
            ("updated", tz_now()),
            ("has_execution_stopped", False),
            ("count_of_retries", 0),
            ("next_retry_at", tz_now()),
            ("seconds_to_next_retry", 1),
        ]
    )

    DEFAULT_IN_BROKER_MESSAGE_PARAMETERS = OrderedDict(
        [
            ("id", uuid4()),
            ("direction", "I"),
            ("app", "APP"),
            ("key", "KEY"),
            ("body", {"key": "value"}),
            ("has_executed", False),
            ("created", tz_now()),
            ("updated", tz_now()),
            ("has_execution_stopped", False),
            ("count_of_retries", 0),
            ("next_retry_at", tz_now()),
            ("seconds_to_next_retry", 1),
        ]
    )

    BROKER_MESSAGE_ADD_QUERY = f"""
                    INSERT INTO {settings.broker_messages_table}
                        (
                            id,
                            direction,
                            app,
                            "key",
                            body,
                            has_executed,
                            created,
                            updated,
                            has_execution_stopped,
                            count_of_retries,
                            next_retry_at,
                            seconds_to_next_retry
                        )
                    VALUES
                        ($1, $2, $3, $4, $5::jsonb, $6, $7, $8, $9, $10, $11, $12);
                    """

    @classmethod
    async def _create_broker_message(
        cls,
        conn,
        id: UUID,
        direction: str,
        app: str,
        key: str,
        body: dict,
        has_executed: bool,
        created: datetime,
        updated: datetime,
        has_execution_stopped: bool,
        count_of_retries: int,
        next_retry_at: datetime,
        seconds_to_next_retry: int,
    ) -> UUID:
        await conn.execute(
            cls.BROKER_MESSAGE_ADD_QUERY,
            id,
            direction,
            app,
            key,
            body,
            has_executed,
            created,
            updated,
            has_execution_stopped,
            count_of_retries,
            next_retry_at,
            seconds_to_next_retry,
        )
        return id

    @classmethod
    async def _create_default_out_broker_message(cls, conn) -> UUID:
        return await cls._create_broker_message(
            conn, *cls.DEFAULT_OUT_BROKER_MESSAGE_PARAMETERS.values()
        )

    @classmethod
    async def _create_default_in_broker_message(cls, conn) -> UUID:
        return await cls._create_broker_message(
            conn, *cls.DEFAULT_IN_BROKER_MESSAGE_PARAMETERS.values()
        )
