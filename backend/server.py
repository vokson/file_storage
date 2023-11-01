from aiohttp import web
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.api import views
from backend.adapters.file_storage.local import LocalFileStorage

file_storage = LocalFileStorage()

@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except Exception as e:
        print('^^^', e)
        response = web.Response(text="Hello, world")
        await response.prepare(request)
        print(response.body)
        print(response.text)
        return response

# @web.middleware
# async def error_middleware(request, handler):
#     print('&&&&&&&&&&&')
#     try:
#         print('&&&&&&&&&&&')
#         response = await handler(request)
#         print('**********')
#         return response
#     except Exception as e:
#         print(e)
#         return web.json_response({'error': str(e)})



async def index(request):
    return web.Response(text="Welcome!")


def setup_routes(app):
    app.router.add_routes([web.get("/", index)])
    app.router.add_view("/files/{id}/", views.FileView, name='Files')


def init():
    # app = web.Application()
    app = web.Application(middlewares=[error_middleware])
    setup_routes(app)
    return app


if __name__ == "__main__":
    web.run_app(init())
