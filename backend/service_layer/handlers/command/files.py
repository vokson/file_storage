import logging
from uuid import uuid4
from typing import AsyncGenerator, Awaitable

from backend.domain import commands
from backend.service_layer.uow import AbstractUnitOfWork
from backend.api.responses.abstract import EmptyResponse
from backend.api.responses.files import FileResponse
from backend.domain.models import File, Link
from backend.core.config import settings, tz_now

logger = logging.getLogger(__name__)

async def get(
    cmd: commands.GetFile,
    uow: AbstractUnitOfWork,
) -> FileResponse:
    async with uow:
        link = Link(
            id=uuid4(),
            file_id=cmd.file_id,
            type=uow.link_repository.DOWNLOAD_LINK_TYPE,
            created=tz_now(),
            expired=tz_now(settings.storage_time_for_links)
        )
        await uow.link_repository.add(link)

        model = await uow.file_repository.get(cmd.account_id, cmd.file_id)
        return FileResponse(**dict(model), download_link=cmd.make_download_url(link.id))

async def download(
    cmd: commands.DownloadFile,
    uow: AbstractUnitOfWork,
) -> tuple[str, int,  Awaitable[AsyncGenerator[bytes, None]]]:
    async with uow:
        model = await uow.file_repository.get(cmd.account_id, cmd.file_id)
        gen = await uow.file_repository.bytes(model.stored_id)

        return model.name, model.size, gen

async def upload(
    cmd: commands.UploadFile,
    uow: AbstractUnitOfWork,
) -> FileResponse:
    async with uow:
        stored_id = uuid4()
        size = await uow.file_repository.store(stored_id, cmd.get_coro_with_bytes_func)

        model = File(
            id=uuid4(),
            account_id=cmd.account_id,
            stored_id=stored_id,
            name=cmd.filename,
            size=size,
            has_deleted=False,
            deleted=None,
            has_erased=False,
            erased=None,
        )

        await uow.file_repository.add(model)
        await uow.commit()
        return FileResponse(**dict(model))

async def delete(
    cmd: commands.DeleteFile,
    uow: AbstractUnitOfWork,
) -> EmptyResponse:
    async with uow:
        await uow.file_repository.delete(cmd.account_id, cmd.file_id)
        await uow.commit()
        return EmptyResponse()

async def erase(
    cmd: commands.EraseFile,
    uow: AbstractUnitOfWork,
) -> EmptyResponse:
    async with uow:
        await uow.file_repository.erase(cmd.file_id)
        await uow.commit()
        return EmptyResponse()