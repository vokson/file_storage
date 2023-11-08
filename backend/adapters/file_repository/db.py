import logging
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

    ADD_QUERY = f"""
                    INSERT INTO {settings.files_table}
                        (
                            account_id,
                            id,
                            stored_id,
                            name,
                            size,
                            created
                        )
                    VALUES
                        ($1, $2, $3, $4, $5, $6);
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
                        account_id = $1 AND
                        id = $2 AND
                        has_stored = TRUE AND
                        has_deleted = FALSE;
                    """

    ERASE_QUERY = f"""
                    UPDATE {settings.files_table}
                    SET has_erased = TRUE, erased = $2
                    WHERE id = $1 AND has_deleted = TRUE AND has_erased = FALSE;
                    """

    def __init__(self, storage: AbstractFileStorage, conn):
        super().__init__(storage)
        self._conn = conn

    async def _get(self, query:str, file_id: UUID) -> File:
        logger.debug(f"Get file with id {file_id}.")
        row = await self._conn.fetchrow(query, file_id)
        if not row:
            raise exceptions.FileNotFound

        return self._convert_row_to_obj(row)

    async def get(self, id: UUID) -> File:
        return await self._get(self.GET_STORED_BY_ID_QUERY, id)

    async def get_not_stored(self, id: UUID) -> File:
        return await self._get(self.GET_BY_ID_QUERY, id)

    async def add(self, account_id: UUID) -> File:
        file_id = uuid4()
        stored_id = uuid4()
        log = (
            f"Add empty file with account_id {account_id}, "
            f"id {file_id}, stored_id {stored_id}"
        )
        logger.info(log)
        await self._conn.execute(
            self.ADD_QUERY, account_id, file_id, stored_id, "", 0, tz_now()
        )
        return await self.get_not_stored(file_id)

    async def bytes(
        self, file_id: UUID
    ) -> Coroutine[None, None, AsyncGenerator[bytes, None]]:
        logger.debug(f"Reading file {file_id}")
        return self._storage.get(file_id)

    async def store(
        self,
        file_id: UUID,
        get_coro_with_bytes_func: Callable[[int], Awaitable[bytearray]],
    ) -> int:
        logger.debug(f"Storing file {file_id}")
        return await self._storage.save(file_id, get_coro_with_bytes_func)

    async def mark_as_stored(self, file_id: UUID, name: str, size: int) -> File:
        logger.debug(f"Mark file {file_id} as stored with name '{name}', size {size}")
        await self._conn.execute(self.STORE_QUERY, file_id, name, size, tz_now())
        return await self.get_not_stored(file_id)

    async def delete(self, account_id: UUID, file_id: UUID):
        logger.info(f"Delete file with id {file_id} by account {account_id}")
        await self._conn.execute(self.DELETE_QUERY, account_id, file_id, tz_now())

    async def erase(self, file_id: UUID):
        logger.debug(f"Erase file with id {file_id}")
        await self._conn.execute(self.ERASE_QUERY, file_id, tz_now())
        await self._storage.erase(file_id)


async def get_db_file_repository(
    storage: AbstractFileStorage, conn
) -> AbstractFileRepository:
    return DatabaseFileRepository(storage, conn)
