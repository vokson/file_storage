from aiohttp import web
from uuid import UUID
from typing import Callable, Awaitable

from backend.api.dependables import get_bus
from backend.api import middlewares
from backend.api.transformers import transform_file_response, transform_json_response
from backend.api.requests.files import (
    GetRequestPath,
    DownloadRequestPath,
    DeleteRequestPath,
)
from backend.domain import commands
from backend.service_layer.message_bus import MessageBus
from ..routes import make_download_url


@middlewares.validate_path_parameters(GetRequestPath)
async def get(
    request: web.Request,
    _account_id: UUID,
    path_parameters: dict,
    bus: MessageBus | None = None,
) -> web.Response:
    bus = bus or await get_bus()

    cmd = commands.GetFile(
        account_id=_account_id,
        file_id=path_parameters["id"],
        make_download_url=make_download_url,
    )
    return await transform_json_response(await bus.handle(cmd))


@middlewares.validate_path_parameters(DownloadRequestPath)
async def download(
    request: web.Request,
    _account_id: UUID,
    path_parameters: dict,
    bus: MessageBus | None = None,
) -> web.StreamResponse:
    bus = bus or await get_bus()

    cmd = commands.DownloadFile(account_id=_account_id, file_id=path_parameters["id"])
    filename, size, gen = await bus.handle(cmd)
    return await transform_file_response(request, filename, size, gen)


@middlewares.validate_file_body()
async def upload(
    request: web.Request,
    _account_id: UUID,
    _filename: str,
    _file: Callable[[int], Awaitable[bytearray]],
    bus: MessageBus | None = None,
) -> web.Response:
    bus = bus or await get_bus()

    cmd = commands.UploadFile(
        account_id=_account_id,
        filename=_filename,
        get_coro_with_bytes_func=_file,
    )
    return await transform_json_response(await bus.handle(cmd))


@middlewares.validate_path_parameters(DeleteRequestPath)
async def delete(
    request: web.Request,
    _account_id: UUID,
    path_parameters: dict,
    bus: MessageBus | None = None,
) -> web.Response:
    bus = bus or await get_bus()

    cmd = commands.DeleteFile(account_id=_account_id, file_id=path_parameters["id"])
    return await transform_json_response(await bus.handle(cmd))
