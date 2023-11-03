import logging
from typing import AsyncGenerator
from backend.api.responses.abstract import Response

from aiohttp import web

from backend.api.codes import RESPONSE_CODES

logger = logging.getLogger(__name__)


def transform_exception(err: Exception) -> web.Response:
    if err.__class__ not in RESPONSE_CODES:
        raise err

    logger.info(err)

    return web.json_response(
        {
            "success": False,
            "code": RESPONSE_CODES[err.__class__],
        },
        status=200,
    )


async def transform_json_response(r: Response) -> web.Response:
    response = web.Response(
        headers={
            "Content-Type": "application/json; charset=utf-8",
        },
        body=r.model_dump_json().encode(encoding='utf-8')
    )
    return response


async def transform_file_response(
    request: web.Request, filename: str, gen: AsyncGenerator[bytes, None]
) -> web.StreamResponse:
    response = web.StreamResponse(
        headers={
            "Content-Type": "application/octet-stream",
            "Content-Disposition": f"attachment; filename={filename}",
        }
    )

    async for chunk in gen:
        if not response.prepared:
            await response.prepare(request)

        await response.write(chunk)

    await response.write_eof()
    return response
