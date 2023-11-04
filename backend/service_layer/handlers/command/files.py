import logging
from typing import AsyncGenerator, Awaitable

from backend.domain import commands
from backend.service_layer.uow import AbstractUnitOfWork
from backend.api.responses.files import FileReponse

logger = logging.getLogger(__name__)

async def get(
    cmd: commands.GetFile,
    uow: AbstractUnitOfWork,
) -> FileReponse:
    async with uow:
        model = await uow.file_repository.get(cmd.account_id, cmd.file_id)
        return FileReponse(**dict(model))

async def download(
    cmd: commands.DownloadFile,
    uow: AbstractUnitOfWork,
) -> tuple[str, int,  Awaitable[AsyncGenerator[bytes, None]]]:
    async with uow:
        model = await uow.file_repository.get(cmd.account_id, cmd.file_id)
        gen = await uow.file_repository.bytes(model.stored_id)

        return model.name, model.size, gen
