import io
import logging
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio

from backend.core import exceptions
from backend.core.config import settings
from backend.tests.src.repository import mixins
from backend.tests.src.storage.mixins import FileOperationMixin

logger = logging.getLogger()


class TestFileRepository(
    mixins.CommonMixin,
    mixins.AccountMixin,
    mixins.FileMixin,
    FileOperationMixin,
):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, rollback_pg):
        self._conn = rollback_pg
        self._account_name, _ = await self._create_default_account(rollback_pg)
        self._file_id = await self._create_default_file(
            rollback_pg, self._account_name
        )
        self._not_stored_file_id = await self._create_default_not_stored_file(
            rollback_pg, self._account_name
        )
        self._deleted_file_id = await self._create_default_deleted_file(
            rollback_pg, self._account_name
        )

    @pytest.mark.asyncio
    async def test_get_by_id(self, rollback_file_repository):
        model = await rollback_file_repository.get(self._file_id)
        self._cmp(self.DEFAULT_FILE_PARAMETERS, model)

    @pytest.mark.asyncio
    async def test_get_by_id_if_not_exist(self, rollback_file_repository):
        with pytest.raises(exceptions.FileNotFound):
            await rollback_file_repository.get(uuid4())

    @pytest.mark.asyncio
    async def test_get_by_id_if_not_stored(self, rollback_file_repository):
        with pytest.raises(exceptions.FileNotFound):
            await rollback_file_repository.get(self._not_stored_file_id)

    @pytest.mark.asyncio
    async def test_get_by_id_if_deleted(self, rollback_file_repository):
        with pytest.raises(exceptions.FileNotFound):
            await rollback_file_repository.get(self._deleted_file_id)

    @pytest.mark.asyncio
    async def test_get_not_stored_by_id(self, rollback_file_repository):
        model = await rollback_file_repository.get_not_stored(
            self._not_stored_file_id
        )
        self._cmp(self.DEFAULT_NOT_STORED_FILE_PARAMETERS, model)

    @pytest.mark.asyncio
    async def test_get_not_stored_by_id_if_not_exist(
        self, rollback_file_repository
    ):
        with pytest.raises(exceptions.FileNotFound):
            await rollback_file_repository.get_not_stored(uuid4())

    @pytest.mark.asyncio
    async def test_add(self, rollback_file_repository):
        name = ""
        size = 0
        query = f"""
                SELECT * FROM {settings.files_table}
                WHERE account_name = $1 AND id = $2 AND name = $3 AND size = $4
                AND created IS NOT NULL
                AND has_stored = FALSE AND stored IS NULL
                AND has_deleted = FALSE AND deleted IS NULL
                AND has_erased = FALSE AND erased IS NULL
                """
        model = await rollback_file_repository.add(self._account_name)
        row = await self._conn.fetchrow(
            query, self._account_name, model.id, name, size
        )

        assert row is not None
        assert model.account_name == self._account_name
        assert model.name == name
        assert model.size == size
        assert model.created is not None
        assert model.stored is None
        assert model.deleted is None
        assert model.erased is None
        assert model.has_stored == False
        assert model.has_deleted == False
        assert model.has_erased == False

    @pytest.mark.asyncio
    async def test_mark_stored(self, rollback_file_repository):
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
        model = await rollback_file_repository.add(self._account_name)
        model = await rollback_file_repository.mark_as_stored(
            model.id, name, size
        )
        row = await self._conn.fetchrow(query, model.id, name, size)

        assert row is not None
        assert model.name == name
        assert model.size == size
        assert model.created is not None
        assert model.stored is not None
        assert model.deleted is None
        assert model.erased is None
        assert model.has_stored == True
        assert model.has_deleted == False
        assert model.has_erased == False

    @pytest.mark.asyncio
    async def test_deleted(self, rollback_file_repository):
        name = "TEST NAME"
        size = 999
        query = f"""
                SELECT * FROM {settings.files_table}
                WHERE id = $1 AND name = $2 AND size = $3
                AND created IS NOT NULL
                AND has_stored = TRUE AND stored IS NOT NULL
                AND has_deleted = TRUE AND deleted IS NOT NULL
                AND has_erased = FALSE AND erased IS NULL
                """
        model = await rollback_file_repository.add(self._account_name)
        model = await rollback_file_repository.mark_as_stored(
            model.id, name, size
        )
        await rollback_file_repository.delete(self._account_name, model.id)
        row = await self._conn.fetchrow(query, model.id, name, size)

        assert row is not None

    @pytest.mark.asyncio
    async def test_erased(self, rollback_file_repository, file_storage):
        name = "TEST NAME"
        data = b"1234567890"
        query = f"""
                SELECT * FROM {settings.files_table}
                WHERE id = $1 AND name = $2 AND size = $3
                AND created IS NOT NULL
                AND has_stored = TRUE AND stored IS NOT NULL
                AND has_deleted = TRUE AND deleted IS NOT NULL
                AND has_erased = TRUE AND erased IS NOT NULL
                """
        model = await rollback_file_repository.add(self._account_name)
        path = file_storage.generate_path(model.stored_id)

        size = await rollback_file_repository.store(
            model.id, self._get_coro_with_bytes(data)
        )
        assert True == Path(path).is_file()

        model = await rollback_file_repository.mark_as_stored(
            model.id, name, size
        )
        await rollback_file_repository.delete(self._account_name, model.id)

        await rollback_file_repository.erase(model.id)
        assert False == Path(path).is_file()

        row = await self._conn.fetchrow(query, model.id, name, size)
        assert row is not None

    @pytest.mark.asyncio
    async def test_take(self, rollback_file_repository, file_storage):
        name = "TEST NAME"
        data = b"1234567890"

        model = await rollback_file_repository.add(self._account_name)
        path = file_storage.generate_path(model.stored_id)

        size = await rollback_file_repository.store(
            model.id, self._get_coro_with_bytes(data)
        )
        assert True == Path(path).is_file()

        model = await rollback_file_repository.mark_as_stored(
            model.id, name, size
        )
        gen = await rollback_file_repository.take(model.id)
        f = io.BytesIO()
        async for chunk in gen:
            f.write(chunk)

        assert data == f.getvalue()
