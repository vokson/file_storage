import logging
from uuid import uuid4
from typing import AsyncGenerator, Awaitable

from backend.domain import commands
from backend.service_layer.uow import AbstractUnitOfWork
from backend.api.responses.abstract import EmptyResponse
from backend.api.responses.files import FileResponse, FileResponseWithLink
from backend.core.config import settings
from backend.core import exceptions

logger = logging.getLogger(__name__)


async def get(
    cmd: commands.GetFile,
    uow: AbstractUnitOfWork,
) -> FileResponseWithLink:
    async with uow:
        link_model = await uow.link_repository.add_download(
            uuid4(), cmd.file_id, settings.storage_time_for_links
        )

        file_model = await uow.file_repository.get(cmd.file_id)
        if file_model.account_id != cmd.account_id:
            raise exceptions.FileNotFound

        await uow.commit()

    return FileResponseWithLink(
        **dict(file_model), link=cmd.make_download_url(link_model.id)
    )


async def add(
    cmd: commands.AddFile,
    uow: AbstractUnitOfWork,
) -> FileResponseWithLink:
    async with uow:
        file_model = await uow.file_repository.add(cmd.account_id)
        link_model = await uow.link_repository.add_upload(
            uuid4(), file_model.id, settings.storage_time_for_links
        )

        await uow.commit()
    return FileResponseWithLink(
        **dict(file_model), link=cmd.make_upload_url(link_model.id)
    )


async def download(
    cmd: commands.DownloadFile,
    uow: AbstractUnitOfWork,
) -> tuple[str, int, Awaitable[AsyncGenerator[bytes, None]]]:
    async with uow:
        link_model = await uow.link_repository.get_download(cmd.link_id)
        file_model = await uow.file_repository.get(link_model.file_id)
        gen = await uow.file_repository.bytes(file_model.stored_id)

        return file_model.name, file_model.size, gen


async def upload(
    cmd: commands.UploadFile,
    uow: AbstractUnitOfWork,
) -> FileResponse:
    async with uow:
        link_model = await uow.link_repository.get_upload(cmd.link_id)
        file_model = await uow.file_repository.get_not_stored(link_model.file_id)
        size = await uow.file_repository.store(
            file_model.stored_id, cmd.get_coro_with_bytes_func
        )

        model = await uow.file_repository.mark_as_stored(
            file_model.id, cmd.filename, size
        )
        await uow.link_repository.delete(cmd.link_id)
        await uow.commit()
        return FileResponse(**dict(model))


async def delete(
    cmd: commands.DeleteFile,
    uow: AbstractUnitOfWork,
) -> EmptyResponse:
    async with uow:
        await uow.file_repository.delete(cmd.account_id, cmd.file_id)
        await uow.link_repository.delete_by_file_id(cmd.file_id)
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
