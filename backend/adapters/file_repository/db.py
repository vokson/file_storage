import logging
from collections.abc import AsyncIterator
from typing import AsyncGenerator, Awaitable, Callable, Coroutine
from uuid import UUID, uuid4

from backend.adapters.file_storage.abstract import AbstractFileStorage
from backend.core import exceptions
from backend.core.config import settings, tz_now
from backend.domain.models import File

from .abstract import AbstractFileRepository

logger = logging.getLogger(__name__)


class DatabaseFileRepository(AbstractFileRepository):
    GET_BY_ID_QUERY = f"SELECT * FROM {settings.files_table} WHERE id = $1;"

    GET_STORED_BY_ID_QUERY = f"""
                    SELECT * FROM {settings.files_table}
                    WHERE id = $1 AND has_stored = TRUE AND has_deleted = FALSE;
                    """

    GET_ALL_STORED_AND_NOT_DELETED_QUERY = f"""
                    SELECT * FROM {settings.files_table}
                    WHERE has_stored = TRUE AND has_deleted = FALSE
                    LIMIT $1 OFFSET $2;
                    """

    GET_DELETED_BY_ID_QUERY = f"""
                    SELECT * FROM {settings.files_table}
                    WHERE id = $1
                    AND has_stored = TRUE
                    AND has_deleted = TRUE
                    AND has_erased = FALSE;
                    """

    GET_ALL_DELETED_AND_NOT_ERASED_QUERY = f"""
                    SELECT * FROM {settings.files_table}
                    WHERE has_deleted = TRUE
                    AND has_erased = FALSE
                    AND deleted < $1;
                    """

    ADD_QUERY = f"""
                    INSERT INTO {settings.files_table}
                        (
                            account_name,
                            id,
                            stored_id,
                            name,
                            size,
                            tag,
                            created
                        )
                    VALUES
                        ($1, $2, $3, $4, $5, $6, $7);
                    """

    STORE_QUERY = f"""
                    UPDATE {settings.files_table}
                    SET
                        name = $2,
                        size = $3,
                        has_stored = TRUE,
                        stored = $4
                    WHERE id = $1 AND has_stored = FALSE;
                    """

    DELETE_QUERY = f"""
                    UPDATE {settings.files_table}
                    SET has_deleted = TRUE, deleted = $3
                    WHERE 
                        account_name = $1 AND
                        id = $2 AND
                        has_stored = TRUE AND
                        has_deleted = FALSE;
                    """

    ERASE_QUERY = f"""
                    UPDATE {settings.files_table}
                    SET has_erased = TRUE, erased = $2
                    WHERE id = $1 AND has_deleted = TRUE AND has_erased = FALSE;
                    """

    GET_ACTUAL_SIZE_BY_ACCOUNT_QUERY = f"""
                    SELECT account_name, SUM(size) as size
                    FROM {settings.files_table}
                    WHERE 
                        has_stored = TRUE AND
                        has_deleted = FALSE
                    GROUP BY account_name;
                    """

    def __init__(self, storage: AbstractFileStorage, conn):
        super().__init__(storage)
        self._conn = conn

    async def _get(self, query: str, file_id: UUID) -> File:
        logger.debug(f"Get file with id {file_id}.")
        row = await self._conn.fetchrow(query, file_id)
        if not row:
            raise exceptions.FileNotFound

        return self._convert_row_to_obj(row)

    async def get(self, id: UUID) -> File:
        return await self._get(self.GET_STORED_BY_ID_QUERY, id)

    async def get_not_stored(self, id: UUID) -> File:
        return await self._get(self.GET_BY_ID_QUERY, id)

    async def get_stored_and_not_deleted(
        self, chunk_size: int, offset: int
    ) -> list[File]:
        logger.debug(f"Get stored and not deleted files.")
        rows = await self._conn.fetch(
            self.GET_ALL_STORED_AND_NOT_DELETED_QUERY, chunk_size, offset
        )
        return [self._convert_row_to_obj(x) for x in rows]

    async def get_deleted(self, id: UUID) -> File:
        return await self._get(self.GET_DELETED_BY_ID_QUERY, id)

    async def get_deleted_and_not_erased(
        self, storage_time_in_sec: int
    ) -> list[File]:
        logger.info(f"Get deleted and not erased files.")
        print(tz_now(-1 * storage_time_in_sec))

        rows = await self._conn.fetch(
            self.GET_ALL_DELETED_AND_NOT_ERASED_QUERY,
            tz_now(-1 * storage_time_in_sec),
        )
        return [self._convert_row_to_obj(x) for x in rows]

    async def add(
        self, account_name: str, tag: str, file_id: UUID | None = None
    ) -> File:
        if file_id is None:
            file_id = uuid4()

        stored_id = uuid4()
        logger.debug(
            f"Add empty file with account name {account_name}, "
            f"id {file_id}, stored_id {stored_id}"
        )
        await self._conn.execute(
            self.ADD_QUERY,
            account_name,
            file_id,
            stored_id,
            "",
            0,
            tag,
            tz_now(),
        )
        return await self.get_not_stored(file_id)

    async def take(
        self, file_id: UUID
    ) -> Coroutine[None, None, AsyncGenerator[bytes, None]]:
        logger.debug(f"Reading file {file_id}")
        model = await self.get(file_id)
        return self._storage.get(model.stored_id)

    async def store(
        self,
        file_id: UUID,
        get_bytes: Callable[[int], Awaitable[bytearray]]
        | Callable[[int], AsyncIterator[bytes]],
    ) -> int:
        logger.debug(f"Storing file {file_id}")
        model = await self.get_not_stored(file_id)
        return await self._storage.save(model.stored_id, get_bytes)

    async def mark_as_stored(
        self, file_id: UUID, name: str, size: int
    ) -> File:
        logger.debug(
            f"Mark file {file_id} as stored with name '{name}', size {size}"
        )
        await self._conn.execute(
            self.STORE_QUERY, file_id, name, size, tz_now()
        )
        return await self.get_not_stored(file_id)

    async def delete(self, account_name: UUID, file_id: UUID) -> File:
        logger.info(f"Delete file with id {file_id} by account {account_name}")
        await self._conn.execute(
            self.DELETE_QUERY, account_name, file_id, tz_now()
        )
        return await self.get_deleted(file_id)

    async def erase(self, file_id: UUID):
        logger.debug(f"Erase file with id {file_id}")
        model = await self.get_deleted(file_id)
        success = await self._storage.erase(model.stored_id)
        if success:
            await self._conn.execute(self.ERASE_QUERY, file_id, tz_now())

    async def get_actual_account_sizes(self) -> list[tuple[str, int]]:
        logger.info(f"Get actual account sizes.")
        rows = await self._conn.fetch(self.GET_ACTUAL_SIZE_BY_ACCOUNT_QUERY)
        return [
            (
                x["account_name"],
                x["size"],
            )
            for x in rows
        ]


async def get_db_file_repository(
    storage: AbstractFileStorage, conn
) -> AbstractFileRepository:
    return DatabaseFileRepository(storage, conn)
