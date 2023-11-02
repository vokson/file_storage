from aiohttp import web

from backend.api.dependables import get_bus
from backend.api.middlewares import validate_path_parameters
from backend.api.transformers import transform_file_response
from backend.api.v1.requests.files import DownloadRequest
from backend.domain import commands
from backend.service_layer.message_bus import MessageBus


@validate_path_parameters(DownloadRequest)
async def download(
    request: web.Request, path_parameters: dict, bus: MessageBus | None = None
) -> web.StreamResponse:
    bus = bus or await get_bus()
    cmd = commands.DownloadFile(**path_parameters)
    return await transform_file_response(request, "text.txt", await bus.handle(cmd))
