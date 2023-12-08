import asyncio
import logging
from typing import AsyncGenerator, Awaitable
from uuid import UUID

import aiohttp

from backend.api.responses.abstract import EmptyResponse
from backend.api.responses.files import (FileResponse, FileResponseWithLink,
                                         NotStoredFileResponse)
from backend.core import exceptions
from backend.core.config import settings
from backend.domain import commands, events, models
from backend.service_layer.uow import AbstractUnitOfWork

logger = logging.getLogger(__name__)


async def get(
    cmd: commands.GetFile,
    uow: AbstractUnitOfWork,
) -> FileResponseWithLink:
    async with uow:
        file_model = await uow.file_repository.get(cmd.file_id)
        if file_model.account_name != cmd.account_name:
            raise exceptions.FileNotFound

        link_model = await uow.link_repository.add_download(
            cmd.file_id, settings.storage_time_for_links
        )

        await uow.commit()

    return FileResponseWithLink(
        **dict(file_model), link=cmd.make_download_url(link_model.id)
    )


async def get_stored_and_not_deleted(
    cmd: commands.GetStoredAndNotDeletedFiles,
    uow: AbstractUnitOfWork,
) -> list[models.File]:
    async with uow:
        return await uow.file_repository.get_stored_and_not_deleted(
            cmd.chunk_size, cmd.offset
        )


async def add(
    cmd: commands.AddFile,
    uow: AbstractUnitOfWork,
) -> NotStoredFileResponse:
    async with uow:
        await uow.account_repository.verify_ready_to_add(
            cmd.account_name, cmd.tag
        )
        file_model = await uow.file_repository.add(cmd.account_name, cmd.tag)
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
        gen = await uow.file_repository.take(file_model.id)

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
        model = await uow.file_repository.delete(cmd.account_name, cmd.file_id)
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


async def erase_deleted(
    cmd: commands.EraseDeletedFiles,
    uow: AbstractUnitOfWork,
):
    async with uow:
        files_to_be_erased = (
            await uow.file_repository.get_deleted_and_not_erased(
                cmd.storage_time_in_sec
            )
        )

        logger.warning("Start to erase files.")

        for file in files_to_be_erased:
            uow.push_message(commands.EraseFile(file.id))
            logger.warning(f"{file.id} has been erased")

        logger.warning(f"Count of erased files: {len(files_to_be_erased)}")


async def clone(
    cmd: commands.CloneFile,
    uow: AbstractUnitOfWork,
):
    from backend.api.routes import make_file_url

    session = None

    async with uow:
        session = uow.session
        #  Проверяем существует ли данный файл
        try:
            await uow.file_repository.get(cmd.file_id)
            return
        except exceptions.FileNotFound:
            pass

        #  Если нет, определяем нужен ли данный файл в данном хранилище
        try:
            account = await uow.account_repository.verify_ready_to_add(
                cmd.account_name, cmd.tag
            )
        except (
            exceptions.AccountNotFound,
            exceptions.TagNotFoundInAccount,
            exceptions.NoSpaceInAccount,
        ):
            return

    #  Если нужен, обращаемся ко всем хранилищам,
    #  чтобы получить ссылку для скачивания

    headers = {"Authorization": str(account.auth_token)}
    download_link = None

    tasks = set()
    for host in settings.other_servers:

        async def get_download_link(file_id: UUID, host: str) -> str | None:
            try:
                response = await session.get(
                    make_file_url(file_id, host=host), headers=headers
                )
                if response.status == 200:
                    json_data = await response.json()

                    nonlocal download_link
                    download_link = json_data["link"]

                    raise exceptions.Ok

            except Exception as e:
                #   Ловим все исключения. При остановке остальные таски
                #   получат Server Disconnected exception
                if isinstance(e, exceptions.Ok):
                    #   Делаем проброс, чтобы asyncio.wait остановился
                    raise e
                else:
                    logger.error(e)

        tasks.add(get_download_link(cmd.file_id, host))

    done, pending = await asyncio.wait(
        tasks, timeout=2.0, return_when=asyncio.FIRST_EXCEPTION
    )

    if download_link is None:
        raise exceptions.NoConnectionToServer

    logger.info(f"File to cloned using download link: {download_link}")

    #  Скачиваем файл, используя полученную ссылку

    response = await session.get(download_link)
    assert response.status == 200

    async with uow:
        model = await uow.file_repository.add(
            cmd.account_name, cmd.tag, cmd.file_id
        )

        size = await uow.file_repository.store(
            model.id, response.content.iter_chunked
        )

        if size != cmd.size:
            raise exceptions.FileSizeError

        model = await uow.file_repository.mark_as_stored(
            model.id, cmd.name, size
        )

        await uow.commit()

    uow.push_message(events.FileStored(model))
