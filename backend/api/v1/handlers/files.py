from aiohttp import web

from backend.api.dependables import get_bus
from backend.api.middlewares import validate_path_parameters
from backend.api.transformers import transform_file_response, transform_json_response
from backend.api.requests.files import GetRequest, DownloadRequest
from backend.domain import commands
from backend.service_layer.message_bus import MessageBus


@validate_path_parameters(GetRequest)
async def get(
    request: web.Request, path_parameters: dict, bus: MessageBus | None = None
) -> web.Response:
    bus = bus or await get_bus()
    cmd = commands.GetFile(**path_parameters)
    return await transform_json_response(await bus.handle(cmd))


@validate_path_parameters(DownloadRequest)
async def download(
    request: web.Request, path_parameters: dict, bus: MessageBus | None = None
) -> web.StreamResponse:
    bus = bus or await get_bus()
    cmd = commands.DownloadFile(**path_parameters)
    return await transform_file_response(request, "text.txt", await bus.handle(cmd))
