import os
import sys

import aiohttp_cors
from aiohttp import web

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.api import middlewares
from backend.api.v1.routes import CORS_ROUTES, ROUTES
from backend.core.config import settings
from backend.service_layer.uow import (close_db_pool, close_http_session,
                                       init_db_pool, init_http_session)


async def startup(app):
    await init_db_pool()
    await init_http_session()


async def cleanup(app):
    await close_db_pool()
    await close_http_session()


def init():
    app = web.Application(middlewares=[middlewares.error_middleware])

    app.router.add_routes(ROUTES)
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                expose_headers="*", allow_headers="*"
            ),
        },
    )

    for method, url, handler in CORS_ROUTES:
        route = cors.add(app.router.add_resource(url))
        cors.add(route.add_route(method, handler))

    app.on_startup.append(startup)
    app.on_cleanup.append(cleanup)
    return app


if __name__ == "__main__":
    web.run_app(init())
