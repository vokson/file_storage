import os
import sys

from aiohttp import web

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.api import middlewares
from backend.api.v1.routes import ROUTES
from backend.core.config import settings
from backend.service_layer.uow import (close_db_pool, close_http_session,
                                       init_db_pool, init_http_session)


async def startup(app):
    await init_db_pool()
    await init_http_session()


async def cleanup(app):
    await close_db_pool()
    await close_http_session()


def setup_routes(app):
    app.router.add_routes(ROUTES)


def init():
    app = web.Application(middlewares=[middlewares.error_middleware])
    setup_routes(app)
    app.on_startup.append(startup)
    app.on_cleanup.append(cleanup)
    return app


if __name__ == "__main__":
    web.run_app(init())
