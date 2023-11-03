import logging
from .abstract import AbstractFileRepository
from backend.domain.models import File
from backend.adapters.file_storage.abstract import AbstractFileStorage
from uuid import UUID
from backend.core import exceptions

logger = logging.getLogger(__name__)


class DatabaseFileRepository(AbstractFileRepository):
    __files_tablename__ = "files"

    # ADD_QUERY = f"""
    #                 INSERT INTO {__files_tablename__}
    #                     (
    #                         id,
    #                         name,
    #                         size,
    #                         user_id,
    #                         has_deleted,
    #                         created,
    #                         updated
    #                     )
    #                 VALUES
    #                     ($1, $2, $3, $4, $5, $6, $7);
    #                 """

    # UPDATE_QUERY = f"""
    #                 UPDATE {__files_tablename__} SET
    #                     (
    #                         name,
    #                         size,
    #                         user_id,
    #                         has_deleted,
    #                         created,
    #                         updated
    #                     ) = (
    #                         $2, $3, $4, $5, $6, $7
    #                     )
    #                 WHERE id = $1;
    #                 """

    GET_BY_ID_QUERY = f"SELECT * FROM {__files_tablename__} WHERE id = $1;"

    def __init__(self, storage: AbstractFileStorage, conn):
        super().__init__(storage)
        self._conn = conn

    async def get(self, id: UUID) -> File:
        logger.debug(f"Get file with id {id}")
        row = await self._conn.fetchrow(self.GET_BY_ID_QUERY, id)
        if not row:
            raise exceptions.FileNotFound

        return self._convert_row_to_obj(row)


async def get_db_file_repository(storage: AbstractFileStorage, conn) -> AbstractFileRepository:
    return DatabaseFileRepository(storage, conn)
