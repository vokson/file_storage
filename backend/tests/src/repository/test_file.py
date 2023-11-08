import logging
from uuid import uuid4

import pytest
import pytest_asyncio

from backend.tests.src.repository import mixins
from backend.core import exceptions
from backend.core.config import settings

logger = logging.getLogger()


class TestFileRepository(
    mixins.CommonMixin, mixins.AccountMixin, mixins.FileMixin
):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, pg):
        self._conn = pg
        self._account_id = await self._create_default_account(pg)
        self._file_id = await self._create_default_file(pg, self._account_id)
        self._not_stored_file_id = await self._create_default_not_stored_file(
            pg, self._account_id
        )
        self._deleted_file_id = await self._create_default_deleted_file(
            pg, self._account_id
        )

    @pytest.mark.asyncio
    async def test_get_by_id(self, file_repository):
        model = await file_repository.get(self._file_id)
        self._cmp(self.DEFAULT_FILE_PARAMETERS, model)

    @pytest.mark.asyncio
    async def test_get_by_id_if_not_exist(self, file_repository):
        with pytest.raises(exceptions.FileNotFound):
            await file_repository.get(uuid4())

    @pytest.mark.asyncio
    async def test_get_by_id_if_not_stored(self, file_repository):
        with pytest.raises(exceptions.FileNotFound):
            await file_repository.get(self._not_stored_file_id)

    @pytest.mark.asyncio
    async def test_get_by_id_if_deleted(self, file_repository):
        with pytest.raises(exceptions.FileNotFound):
            await file_repository.get(self._deleted_file_id)

    @pytest.mark.asyncio
    async def test_get_not_stored_by_id(self, file_repository):
        model = await file_repository.get_not_stored(self._not_stored_file_id)
        self._cmp(self.DEFAULT_NOT_STORED_FILE_PARAMETERS, model)

    @pytest.mark.asyncio
    async def test_get_not_stored_by_id_if_not_exist(self, file_repository):
        with pytest.raises(exceptions.FileNotFound):
            await file_repository.get_not_stored(uuid4())

    @pytest.mark.asyncio
    async def test_add(self, file_repository):
        name = ""
        size = 0
        query = f"""
                SELECT * FROM {settings.files_table}
                WHERE account_id = $1 AND id = $2 AND name = $3 AND size = $4
                AND created IS NOT NULL
                AND has_stored = FALSE AND stored IS NULL
                AND has_deleted = FALSE AND deleted IS NULL
                AND has_erased = FALSE AND erased IS NULL
                """
        model = await file_repository.add(self._account_id)
        row = await self._conn.fetchrow(
            query, self._account_id, model.id, name, size
        )

        assert row is not None
        assert model.account_id == self._account_id
        assert model.name == name
        assert model.size == size
        assert model.has_stored == False
        assert model.has_deleted == False
        assert model.has_erased == False

    @pytest.mark.asyncio
    async def test_mark_stored(self, file_repository):
        name = "TEST NAME"
        size = 999
        query = f"""
                SELECT * FROM {settings.files_table}
                WHERE id = $1 AND name = $2 AND size = $3
                AND created IS NOT NULL
                AND has_stored = TRUE AND stored IS NOT NULL
                AND has_deleted = FALSE AND deleted IS NULL
                AND has_erased = FALSE AND erased IS NULL
                """
        model = await file_repository.add(self._account_id)
        model = await file_repository.mark_as_stored(model.id, name, size)
        row = await self._conn.fetchrow(query, model.id, name, size)

        assert row is not None
        assert model.name == name
        assert model.size == size
        assert model.has_stored == True
        assert model.has_deleted == False
        assert model.has_erased == False
