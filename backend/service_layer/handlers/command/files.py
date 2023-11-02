import logging
from typing import AsyncGenerator, Awaitable

from backend.domain import commands
from backend.service_layer.uow import AbstractUnitOfWork

logger = logging.getLogger(__name__)


async def download(
    cmd: commands.DownloadFile,
    uow: AbstractUnitOfWork,
) -> Awaitable[AsyncGenerator[bytes, None]]:
    return uow.file_storage.get(cmd.id)

