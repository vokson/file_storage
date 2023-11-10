import logging
from uuid import uuid4

import pytest
import pytest_asyncio

from backend.core import exceptions
from backend.core.config import settings
from backend.tests.src.repository import mixins

logger = logging.getLogger()


class TestLinkRepository(
    mixins.CommonMixin, mixins.AccountMixin, mixins.LinkMixin, mixins.FileMixin
):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, rollback_pg):
        self._conn = rollback_pg
        self._account_id, _ = await self._create_default_account(rollback_pg)
        self._file_id = await self._create_default_file(rollback_pg, self._account_id)

    @pytest.mark.asyncio
    async def test_get_download(self, rollback_link_repository):
        link_id = await self._create_default_download_link(
            self._conn, self._file_id
        )
        model = await rollback_link_repository.get_download(link_id)

        self._cmp(self.DEFAULT_DOWNLOAD_LINK_PARAMETERS, model)

    @pytest.mark.asyncio
    async def test_get_download_if_not_exist(self, rollback_link_repository):
        with pytest.raises(exceptions.FileNotFound):
            await rollback_link_repository.get_download(uuid4())

    @pytest.mark.asyncio
    async def test_get_upload(self, rollback_link_repository):
        link_id = await self._create_default_upload_link(
            self._conn, self._file_id
        )
        model = await rollback_link_repository.get_upload(link_id)

        self._cmp(self.DEFAULT_UPLOAD_LINK_PARAMETERS, model)

    @pytest.mark.asyncio
    async def test_get_upload_if_not_exist(self, rollback_link_repository):
        with pytest.raises(exceptions.FileNotFound):
            await rollback_link_repository.get_upload(uuid4())

    @pytest.mark.asyncio
    async def test_add_download(self, rollback_link_repository):
        expire_period_in_sec = 100
        model = await rollback_link_repository.add_download(
            self._file_id, expire_period_in_sec
        )

        query = f"""
                SELECT * FROM {settings.links_table}
                WHERE file_id = $1 AND id = $2 AND type = 'D';
                """
        row = await self._conn.fetchrow(query, self._file_id, model.id)

        assert row is not None
        assert model.file_id == self._file_id
        assert (
            int((model.expired - model.created).total_seconds())
            == expire_period_in_sec
        )

    @pytest.mark.asyncio
    async def test_add_upload(self, rollback_link_repository):
        expire_period_in_sec = 100
        model = await rollback_link_repository.add_upload(
            self._file_id, expire_period_in_sec
        )

        query = f"""
                SELECT * FROM {settings.links_table}
                WHERE file_id = $1 AND id = $2 AND type = 'U';
                """
        row = await self._conn.fetchrow(query, self._file_id, model.id)

        assert row is not None
        assert model.file_id == self._file_id
        assert (
            int((model.expired - model.created).total_seconds())
            == expire_period_in_sec
        )

    @pytest.mark.asyncio
    async def test_delete_by_link_id(self, rollback_link_repository):
        query = f"SELECT * FROM {settings.links_table} WHERE id = $1;"

        link_id = await self._create_default_download_link(
            self._conn, self._file_id
        )
        await rollback_link_repository.delete(link_id)

        row = await self._conn.fetchrow(query, link_id)
        assert row is None

        link_id = await self._create_default_upload_link(
            self._conn, self._file_id
        )
        await rollback_link_repository.delete(link_id)

        row = await self._conn.fetchrow(query, link_id)
        assert row is None

    @pytest.mark.asyncio
    async def test_delete_by_link_id_if_not_exist(self, rollback_link_repository):
        query = f"SELECT * FROM {settings.links_table};"

        await self._create_default_download_link(self._conn, self._file_id)
        await self._create_default_upload_link(self._conn, self._file_id)
        await rollback_link_repository.delete(uuid4())

        rows = await self._conn.fetch(query)
        assert len(rows) == 2

    @pytest.mark.asyncio
    async def test_delete_by_file_id(self, rollback_link_repository):
        query = f"SELECT * FROM {settings.links_table} WHERE file_id = $1;"

        await self._create_default_download_link(self._conn, self._file_id)
        await self._create_default_upload_link(self._conn, self._file_id)
        await rollback_link_repository.delete_by_file_id(self._file_id)

        row = await self._conn.fetchrow(query, self._file_id)
        assert row is None

    @pytest.mark.asyncio
    async def test_delete_by_file_id_if_not_exist(self, rollback_link_repository):
        query = f"SELECT * FROM {settings.links_table};"

        await self._create_default_download_link(self._conn, self._file_id)
        await self._create_default_upload_link(self._conn, self._file_id)
        await rollback_link_repository.delete_by_file_id(uuid4())

        rows = await self._conn.fetch(query)
        assert len(rows) == 2