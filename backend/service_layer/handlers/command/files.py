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
        model = await uow.file_repository.get(cmd.id)
        return FileReponse(**dict(model))

async def download(
    cmd: commands.DownloadFile,
    uow: AbstractUnitOfWork,
) -> Awaitable[AsyncGenerator[bytes, None]]:
    return uow.file_repository.bytes(cmd.id)

