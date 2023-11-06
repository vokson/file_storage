from aiohttp import web

from backend.api.transformers import transform_json_response
from backend.api.responses.abstract import EmptyResponse


async def echo(
    request: web.Request, **kwargs
) -> web.Response:
    return await transform_json_response(EmptyResponse())
