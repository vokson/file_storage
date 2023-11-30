import io
import logging
from contextlib import nullcontext as no_exception
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from aiohttp import FormData

from backend.api.responses.files import (FileResponse, FileResponseWithLink,
                                         NotStoredFileResponse)
from backend.core import exceptions
from backend.core.config import settings
from backend.domain.models import File
from backend.tests.src.repository.mixins import AccountMixin
from backend.tests.src.storage.mixins import FileOperationMixin
from backend.tests.src.integration.mixins import CleanDatabaseMixin

logger = logging.getLogger()


class TestFileEndpoints(CleanDatabaseMixin, FileOperationMixin, AccountMixin):
    DEFAULT_FILENAME = "FILENAME"
    DEFAULT_FILESIZE = 100

    def _files_url(self):
        return f"{self._base_url}/files/"

    def _files_item_url(self, id: UUID):
        return f"{self._files_url()}{id}/"

    async def _create_default_file(self, file_rep) -> File:
        async with self._conn.transaction():
            model = await file_rep.add(self._account_name)
            return await file_rep.mark_as_stored(
                model.id, self.DEFAULT_FILENAME, self.DEFAULT_FILESIZE
            )

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, pg):
        self._conn = pg
        await self.clean_db()
        async with self._conn.transaction():
            (
                self._account_name,
                self._auth_token,
            ) = await self._create_default_account(pg)

        self._base_url = settings.server
        self._headers = {"Authorization": str(self._auth_token)}

    @pytest.mark.asyncio
    async def test_get(self, session, file_repository):
        model = await self._create_default_file(file_repository)

        async with session.get(
            self._files_item_url(model.id), headers=self._headers
        ) as r:
            assert r.status == 200

            with no_exception():
                response_model = FileResponseWithLink(**await r.json())

        assert response_model.id == model.id
        assert response_model.name == self.DEFAULT_FILENAME
        assert response_model.size == self.DEFAULT_FILESIZE

        await self.clean_db()

    @pytest.mark.asyncio
    async def test_get_if_not_exist(self, session):
        async with session.get(
            self._files_item_url(uuid4()), headers=self._headers
        ) as r:
            assert r.status == 404
            assert await r.text() == "File.Error.NotFound"

        await self.clean_db()

    @pytest.mark.asyncio
    async def test_delete(self, session, file_repository):
        model = await self._create_default_file(file_repository)

        async with session.delete(
            self._files_item_url(model.id), headers=self._headers
        ) as r:
            assert r.status == 204

        with pytest.raises(exceptions.FileNotFound):
            await file_repository.get(model.id)

        await self.clean_db()

    @pytest.mark.asyncio
    async def test_delete_if_not_exist(self, session):
        async with session.delete(
            self._files_item_url(uuid4()), headers=self._headers
        ) as r:
            assert r.status == 404
            assert await r.text() == "File.Error.NotFound"

        await self.clean_db()

    @pytest.mark.asyncio
    async def test_upload_and_download(self, session):
        #  TAKE UPLOAD URL
        async with session.post(self._files_url(), headers=self._headers) as r:
            assert r.status == 200
            response_model = NotStoredFileResponse(**await r.json())
            upload_link = response_model.link
            file_id = response_model.id

        #  UPLOADING
        data = b"1234567890"
        form = FormData()
        form.add_field(
            "file",
            data,
            filename=self.DEFAULT_FILENAME,
        )
        async with session.post(upload_link, data=form) as r:
            assert r.status == 200
            response_model = FileResponse(**await r.json())

        #  TAKE DOWNLOAD URL
        async with session.get(
            self._files_item_url(file_id), headers=self._headers
        ) as r:
            assert r.status == 200
            response_model = FileResponseWithLink(**await r.json())
            download_link = response_model.link

        #  DOWNLOADING
        async with session.get(download_link) as r:
            assert r.status == 200
            content_length = int(r.headers["Content-Length"])

            f = io.BytesIO()
            f.write(await r.content.read(content_length))
            assert data == f.getvalue()

        await self.clean_db()
