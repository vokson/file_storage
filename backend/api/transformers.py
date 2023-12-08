import urllib.parse
import logging
from typing import AsyncGenerator

from aiohttp import web

from backend.api.codes import RESPONSE_CODES
from backend.api.responses.abstract import Response

logger = logging.getLogger(__name__)


def transform_exception(err: Exception) -> web.Response:
    if err.__class__ not in RESPONSE_CODES:
        raise err

    status, code = RESPONSE_CODES[err.__class__]

    return web.Response(text=code, status=status)


async def transform_json_response(
    r: Response | list[Response], status: int = 200
) -> web.Response:
    response = web.Response(
        headers={
            "Content-Type": "application/json; charset=utf-8",
        },
        body=f"[{','.join([x.model_dump_json() for x in r])}]"
        if type(r) is list
        else r.model_dump_json(),
        status=status,
    )
    return response


async def transform_file_response(
    request: web.Request,
    filename: str,
    size: int,
    gen: AsyncGenerator[bytes, None],
) -> web.StreamResponse:
    response = web.StreamResponse(
        headers={
            "Content-Type": "application/octet-stream",
            "Content-Length": str(size),
            "Content-Disposition": f"attachment; filename*=utf-8''{urllib.parse.quote(filename)}",
        }
    )

    async for chunk in gen:
        if not response.prepared:
            await response.prepare(request)

        await response.write(chunk)

    await response.write_eof()
    return response
