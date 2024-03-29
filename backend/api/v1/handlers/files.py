from typing import Awaitable, Callable
from uuid import UUID

from aiohttp import web

from backend.api import middlewares
from backend.api.dependables import get_bus
from backend.api.requests.files import (DeleteRequestPath, DownloadRequestPath,
                                        GetRequestPath, PostRequestBody,
                                        UploadRequestPath)
from backend.api.transformers import (transform_file_response,
                                      transform_json_response)
from backend.domain import commands
from backend.service_layer.message_bus import MessageBus


@middlewares.verify_auth_token()
@middlewares.validate_path_parameters(GetRequestPath)
async def get(
    request: web.Request,
    _account_name: str,
    _path_parameters: dict,
    bus: MessageBus | None = None,
) -> web.Response:
    bus = bus or await get_bus()
    from ..routes import make_download_url

    cmd = commands.GetFile(
        account_name=_account_name,
        file_id=_path_parameters["file_id"],
        make_download_url=make_download_url,
    )
    return await transform_json_response(await bus.handle(cmd))


@middlewares.verify_auth_token()
@middlewares.validate_json_body(PostRequestBody)
async def post(
    request: web.Request,
    _account_name: str,
    _body: PostRequestBody,
    bus: MessageBus | None = None,
) -> web.Response:
    bus = bus or await get_bus()
    from ..routes import make_upload_url

    cmd = commands.AddFile(
        account_name=_account_name,
        make_upload_url=make_upload_url,
        tag=_body.tag,
    )
    return await transform_json_response(await bus.handle(cmd))


@middlewares.validate_path_parameters(DownloadRequestPath)
async def download(
    request: web.Request,
    _path_parameters: dict,
    bus: MessageBus | None = None,
) -> web.StreamResponse:
    bus = bus or await get_bus()

    cmd = commands.DownloadFile(link_id=_path_parameters["link_id"])
    filename, size, gen = await bus.handle(cmd)
    return await transform_file_response(request, filename, size, gen)


@middlewares.validate_path_parameters(UploadRequestPath)
@middlewares.validate_file_body()
async def upload(
    request: web.Request,
    _path_parameters: dict,
    _filename: str,
    _file: Callable[[int], Awaitable[bytearray]],
    bus: MessageBus | None = None,
) -> web.Response:
    bus = bus or await get_bus()

    cmd = commands.UploadFile(
        link_id=_path_parameters["link_id"],
        filename=_filename,
        get_coro_with_bytes_func=_file,
    )
    return await transform_json_response(await bus.handle(cmd))


@middlewares.verify_auth_token()
@middlewares.validate_path_parameters(DeleteRequestPath)
async def delete(
    request: web.Request,
    _account_name: str,
    _path_parameters: dict,
    bus: MessageBus | None = None,
) -> web.Response:
    bus = bus or await get_bus()

    cmd = commands.DeleteFile(
        account_name=_account_name, file_id=_path_parameters["file_id"]
    )
    return await transform_json_response(await bus.handle(cmd), status=204)
