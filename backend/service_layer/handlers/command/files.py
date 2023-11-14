import asyncio
import logging
from contextlib import suppress
from typing import AsyncGenerator, Awaitable
from uuid import UUID

import aiohttp

from backend.api.responses.abstract import EmptyResponse
from backend.api.responses.files import (FileResponse, FileResponseWithLink,
                                         NotStoredFileResponse)
from backend.core import exceptions
from backend.core.config import settings
from backend.domain import commands, events
from backend.service_layer.uow import AbstractUnitOfWork

logger = logging.getLogger(__name__)


async def get(
    cmd: commands.GetFile,
    uow: AbstractUnitOfWork,
) -> FileResponseWithLink:
    async with uow:
        file_model = await uow.file_repository.get(cmd.file_id)
        if file_model.account_id != cmd.account_id:
            raise exceptions.FileNotFound

        link_model = await uow.link_repository.add_download(
            cmd.file_id, settings.storage_time_for_links
        )

        await uow.commit()

    return FileResponseWithLink(
        **dict(file_model), link=cmd.make_download_url(link_model.id)
    )


async def add(
    cmd: commands.AddFile,
    uow: AbstractUnitOfWork,
) -> NotStoredFileResponse:
    async with uow:
        file_model = await uow.file_repository.add(cmd.account_id)
        link_model = await uow.link_repository.add_upload(
            file_model.id, settings.storage_time_for_links
        )

        await uow.commit()
    return NotStoredFileResponse(
        **dict(file_model), link=cmd.make_upload_url(link_model.id)
    )


async def download(
    cmd: commands.DownloadFile,
    uow: AbstractUnitOfWork,
) -> tuple[str, int, Awaitable[AsyncGenerator[bytes, None]]]:
    async with uow:
        link_model = await uow.link_repository.get_download(cmd.link_id)
        file_model = await uow.file_repository.get(link_model.file_id)
        gen = await uow.file_repository.bytes(file_model.id)

        return file_model.name, file_model.size, gen


async def upload(
    cmd: commands.UploadFile,
    uow: AbstractUnitOfWork,
) -> FileResponse:
    async with uow:
        link_model = await uow.link_repository.get_upload(cmd.link_id)
        file_model = await uow.file_repository.get_not_stored(
            link_model.file_id
        )
        size = await uow.file_repository.store(
            file_model.id, cmd.get_coro_with_bytes_func
        )

        model = await uow.file_repository.mark_as_stored(
            file_model.id, cmd.filename, size
        )
        await uow.link_repository.delete(cmd.link_id)
        await uow.commit()

    uow.push_message(events.FileStored(model))
    return FileResponse(**dict(model))


async def delete(
    cmd: commands.DeleteFile,
    uow: AbstractUnitOfWork,
) -> EmptyResponse:
    async with uow:
        await uow.file_repository.get(cmd.file_id)
        model = await uow.file_repository.delete(cmd.account_id, cmd.file_id)
        await uow.link_repository.delete_by_file_id(cmd.file_id)
        await uow.commit()

    uow.push_message(events.FileDeleted(model))
    return EmptyResponse()


async def erase(
    cmd: commands.EraseFile,
    uow: AbstractUnitOfWork,
) -> EmptyResponse:
    async with uow:
        await uow.file_repository.erase(cmd.file_id)
        await uow.commit()
        return EmptyResponse()


async def clone(
    cmd: commands.CloneFile,
    uow: AbstractUnitOfWork,
):
    from backend.api.routes import make_file_url

    async with uow:
        #  Проверяем существует ли данный файл
        try:
            await uow.file_repository.get(cmd.file_id)
            return
        except exceptions.FileNotFound:
            pass

        #  Если нет, определяем нужен ли данный файл в данном хранилище
        try:
            account = await uow.account_repository.get_by_id(cmd.account_id)
        except exceptions.AccountNotFound:
            return

        if not account.is_active:
            return

    #  Если нужен, обращаемся ко всем хранилищам,
    #  чтобы получить ссылку для скачивания

    headers = {"Authorization": str(account.auth_token)}
    hosts = ['10.95.27.163:8080']

    session = aiohttp.ClientSession()
    download_link = None

    tasks = set()
    for host in hosts:
        async def get_download_link(file_id: UUID, host: str) -> str | None:
            response = await session.get(make_file_url(file_id, host=host), headers=headers)
            if response.status == 200:
                json_data = await response.json()

                nonlocal download_link
                download_link = json_data['link']

                raise exceptions.Ok
            

        tasks.add(get_download_link(cmd.file_id, host))

    # done, pending = asyncio.wait(tasks, timeout=2, return_when=asyncio.FIRST_EXCEPTION)


    loop = asyncio.get_event_loop()
    done, pending = loop.run_until_complete(
        asyncio.wait(tasks, timeout=2.0, return_when=asyncio.FIRST_EXCEPTION)
    )
    # for coro in done_first:
    #     try:
    #         print(coro.result())
    #     except TimeoutError:
    #         print("cleanup after error before exit")

    for p in pending:
        p.cancel()
        with suppress(asyncio.CancelledError):
            loop.run_until_complete(p)

    print('LINK: ', download_link)

    await session.close()
