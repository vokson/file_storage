import logging
from uuid import uuid4
from typing import AsyncGenerator, Awaitable

from backend.domain import commands
from backend.service_layer.uow import AbstractUnitOfWork
from backend.api.responses.files import FileResponse
from backend.domain.models import File

logger = logging.getLogger(__name__)

async def get(
    cmd: commands.GetFile,
    uow: AbstractUnitOfWork,
) -> FileResponse:
    async with uow:
        model = await uow.file_repository.get(cmd.account_id, cmd.file_id)
        return FileResponse(**dict(model))

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


    # with open(os.path.join('/spool/yarrr-media/mp3/', filename), 'wb') as f:
    #     while True:
    #         chunk = await field.read_chunk()  # 8192 bytes by default.
    #         if not chunk:
    #             break
    #         size += len(chunk)
    #         f.write(chunk)
