from aiohttp import web

from .handlers import files

ROUTES = [
    web.get("/files/{id}/", files.get),
    web.get("/files/{id}/download/", files.download),
]