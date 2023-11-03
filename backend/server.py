import os
import sys

from aiohttp import web

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.api.middlewares import error_middleware
from backend.api.v1.handlers import files
from backend.core.config import settings



# async def index(request):
#     response = web.Response(text="Welcome")
#     x = 1 / 0
#     return response


def setup_routes(app):
    app.router.add_routes([web.get("/files/{id}/", files.download)])


def init():
    app = web.Application(middlewares=[error_middleware])
    setup_routes(app)
    return app


if __name__ == "__main__":
    web.run_app(init())
