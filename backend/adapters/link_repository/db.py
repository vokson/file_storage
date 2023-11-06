import logging
from .abstract import AbstractLinkRepository
from backend.domain.models import Link
from backend.core.config import settings, tz_now
from backend.core import exceptions

logger = logging.getLogger(__name__)


class DatabaseLinkRepository(AbstractLinkRepository):
    ADD_QUERY = f"""
                    INSERT INTO {settings.links_table}
                        (
                            id,
                            file_id,
                            type,
                            created,
                            expired
                        )
                    VALUES
                        ($1, $2, $3, $4, $5);
                    """


    def __init__(self, conn):
        self._conn = conn

    async def add(self, model: Link):
        logger.debug(f"Add link {dict(model)}")
        await self._conn.execute(
            self.ADD_QUERY,
            model.id,
            model.file_id,
            model.type,
            model.created,
            model.expired
        )

#     async def add(self, model: File):
#         logger.debug(f"Add file {dict(model)}")
#         await self._conn.execute(
#             self.ADD_QUERY,
#             model.id,
#             model.stored_id,
#             model.name,
#             model.size,
#             model.created,
#             model.has_deleted,
#             model.deleted,
#             model.has_erased,
#             model.erased,
#             model.account_id,
#         )

#     async def bytes(
#         self, file_id: UUID
#     ) -> Coroutine[None, None, AsyncGenerator[bytes, None]]:
#         logger.debug(f"Reading file {file_id}")
#         return self._storage.get(file_id)

#     async def store(
#         self,
#         file_id: UUID,
#         get_coro_with_bytes_func: Callable[[int], Awaitable[bytearray]],
#     ) -> int:
#         logger.debug(f"Storing file {file_id}")
#         return await self._storage.save(file_id, get_coro_with_bytes_func)

#     async def delete(self, account_id: UUID, file_id: UUID):
#         logger.info(f"Delete file with id {file_id} by account {account_id}")
#         await self._conn.execute(self.DELETE_QUERY, account_id, file_id, tz_now())

#     async def erase(self, file_id: UUID):
#         logger.debug(f"Erase file with id {file_id}")
#         await self._conn.execute(self.ERASE_QUERY, file_id, tz_now())
#         await self._storage.erase(file_id)


async def get_db_link_repository(conn) -> AbstractLinkRepository:
    return DatabaseLinkRepository(conn)
