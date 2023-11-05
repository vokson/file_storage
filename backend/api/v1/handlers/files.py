from aiohttp import web
from uuid import UUID

from backend.api.dependables import get_bus
from backend.api.middlewares import validate_path_parameters
from backend.api.transformers import transform_file_response, transform_json_response
from backend.api.requests.files import GetRequest, DownloadRequest
from backend.domain import commands
from backend.service_layer.message_bus import MessageBus


@validate_path_parameters(GetRequest)
async def get(
    request: web.Request,
    _account_id: UUID,
    path_parameters: dict,
    bus: MessageBus | None = None,
) -> web.Response:
    bus = bus or await get_bus()
    cmd = commands.GetFile(account_id=_account_id, file_id=path_parameters["id"])
    return await transform_json_response(await bus.handle(cmd))


@validate_path_parameters(DownloadRequest)
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


async def upload(
    request: web.Request, _account_id: UUID, bus: MessageBus | None = None
) -> web.Response:
    bus = bus or await get_bus()
    reader = await request.multipart()
    field = await reader.next()
    assert field.name == "file"

    cmd = commands.UploadFile(
        account_id=_account_id, filename=field.filename, get_coro_with_bytes_func=field.read_chunk
    )
    return await transform_json_response(await bus.handle(cmd))

