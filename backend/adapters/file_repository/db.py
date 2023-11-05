import logging
from .abstract import AbstractFileRepository
from backend.domain.models import File
from backend.adapters.file_storage.abstract import AbstractFileStorage
from uuid import UUID
from typing import AsyncGenerator, Coroutine, Awaitable, Callable
from backend.core.config import settings
from backend.core import exceptions

logger = logging.getLogger(__name__)


class DatabaseFileRepository(AbstractFileRepository):
    ADD_QUERY = f"""
                    INSERT INTO {settings.files_table}
                        (
                            id,
                            stored_id,
                            name,
                            size,
                            created,
                            has_deleted,
                            deleted,
                            has_erased,
                            erased,
                            account_id
                        )
                    VALUES
                        ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10);
                    """

    GET_BY_ID_QUERY = f"""
                    SELECT * FROM {settings.files_table}
                    WHERE account_id = $1 AND id = $2;
                    """

    def __init__(self, storage: AbstractFileStorage, conn):
        super().__init__(storage)
        self._conn = conn

    async def get(self, account_id: UUID, file_id: UUID) -> File:
        logger.debug(f"Get file with id {file_id} by account {account_id}")
        row = await self._conn.fetchrow(self.GET_BY_ID_QUERY, account_id, file_id)
        if not row:
            raise exceptions.FileNotFound

        return self._convert_row_to_obj(row)

    async def add(self, model: File):
        logger.debug(f"Add file {dict(model)}")
        await self._conn.execute(
            self.ADD_QUERY,
            model.id,
            model.stored_id,
            model.name,
            model.size,
            model.created,
            model.has_deleted,
            model.deleted,
            model.has_erased,
            model.erased,
            model.account_id
        )

    async def bytes(
        self, file_id: UUID
    ) -> Coroutine[None, None, AsyncGenerator[bytes, None]]:
        logger.debug(f"Reading file {file_id}")
        return self._storage.get(file_id)

    async def store(
        self,
        file_id: UUID,
        # bytes_gen: AsyncGenerator[bytes, None],
        get_coro_with_bytes_func: Callable[[int], Awaitable[bytearray]]
    ) -> int:
        logger.debug(f"Storing file {file_id}")
        return await self._storage.save(file_id, get_coro_with_bytes_func)


async def get_db_file_repository(
    storage: AbstractFileStorage, conn
) -> AbstractFileRepository:
    return DatabaseFileRepository(storage, conn)
