import os
import sys

from aiohttp import web

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.core.config import settings
from backend.api import middlewares
from backend.api.v1.routes import ROUTES



def setup_routes(app):
    app.router.add_routes(ROUTES)


def init():
    app = web.Application(
        middlewares=[middlewares.error_middleware]
    )
    setup_routes(app)
    return app


if __name__ == "__main__":
    web.run_app(init())
