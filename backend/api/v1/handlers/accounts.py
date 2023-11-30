from aiohttp import web

from backend.api.dependables import get_bus
from backend.api.transformers import transform_json_response
from backend.domain import commands
from backend.service_layer.message_bus import MessageBus


async def get(
    request: web.Request,
    bus: MessageBus | None = None,
) -> web.Response:
    bus = bus or await get_bus()

    cmd = commands.GetAccounts()
    return await transform_json_response(await bus.handle(cmd))
