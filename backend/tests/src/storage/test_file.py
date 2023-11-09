import io
import logging
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio

from backend.tests.src.storage import mixins

logger = logging.getLogger()


class TestFileStorage(mixins.FileOperationMixin):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self._data = b"1234567890"

    @pytest.mark.asyncio
    async def test_get(self, file_storage):
        id = uuid4()
        path = file_storage.generate_path(id)
        self._save(path, self._data)

        gen = file_storage.get(id)
        f = io.BytesIO()
        async for chunk in gen:
            f.write(chunk)

        assert self._data == f.getvalue()

    @pytest.mark.asyncio
    async def test_save(self, file_storage):
        id = uuid4()
        path = file_storage.generate_path(id)
        await file_storage.save(id, self._get_coro_with_bytes(self._data))

        with open(path, mode="rb") as f:
            stored_data = f.read()

        assert stored_data == self._data

    @pytest.mark.asyncio
    async def test_erase(self, file_storage):
        id = uuid4()
        path = file_storage.generate_path(id)
        self._save(path, self._data)

        assert True == Path(path).is_file()

        await file_storage.erase(id)
        assert False == Path(path).is_file()
