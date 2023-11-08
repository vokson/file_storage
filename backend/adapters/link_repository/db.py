import logging
from uuid import UUID

from backend.core import exceptions
from backend.core.config import settings, tz_now
from backend.domain.models import Link

from .abstract import AbstractLinkRepository

logger = logging.getLogger(__name__)


class DatabaseLinkRepository(AbstractLinkRepository):
    GET_BY_ID_QUERY = f"""
                    SELECT * FROM {settings.links_table}
                    WHERE id = $1 AND expired > now() AND type = $2;
                    """

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

    DELETE_BY_ID_QUERY = f"DELETE FROM {settings.links_table} WHERE id = $1;"
    DELETE_BY_FILE_ID_QUERY = f"DELETE FROM {settings.links_table} WHERE file_id = $1;"


    async def _get(self, link_id: UUID, link_type: str) -> Link:
        logger.debug(f"Get link with id {link_id} and type {link_type}.")
        row = await self._conn.fetchrow(self.GET_BY_ID_QUERY, link_id, link_type)
        if not row:
            raise exceptions.FileNotFound

        return self._convert_row_to_obj(row)

    async def get_download(self, link_id: UUID) -> Link:
        return await self._get(link_id, self.DOWNLOAD_LINK_TYPE)

    async def get_upload(self, link_id: UUID) -> Link:
        return await self._get(link_id, self.UPLOAD_LINK_TYPE)

    async def _add(
        self, link_id: UUID, file_id: UUID, link_type: str, expire_period_in_sec: int
    ) -> Link:
        logger.debug(
            f"""
                    Add link with id {link_id}, file_id {file_id},
                    type {link_type}, expire period {expire_period_in_sec}
                    """
        )

        await self._conn.execute(
            self.ADD_QUERY,
            link_id,
            file_id,
            link_type,
            tz_now(),
            tz_now(expire_period_in_sec),
        )
        return await self._get(link_id, link_type)

    async def add_download(
        self, link_id: UUID, file_id: UUID, expire_period_in_sec: int
    ) -> Link:
        return await self._add(
            link_id, file_id, self.DOWNLOAD_LINK_TYPE, expire_period_in_sec
        )

    async def add_upload(
        self, link_id: UUID, file_id: UUID, expire_period_in_sec: int
    ) -> Link:
        return await self._add(
            link_id, file_id, self.UPLOAD_LINK_TYPE, expire_period_in_sec
        )

    async def delete(self, link_id: UUID):
        logger.debug(f"Delete link with id {link_id}")
        await self._conn.execute(self.DELETE_BY_ID_QUERY, link_id)

    async def delete_by_file_id(self, file_id: UUID):
        logger.debug(f"Delete link with file_id {file_id}")
        await self._conn.execute(self.DELETE_BY_FILE_ID_QUERY, file_id)


async def get_db_link_repository(conn) -> AbstractLinkRepository:
    return DatabaseLinkRepository(conn)
