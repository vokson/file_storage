from aiohttp import web
from uuid import UUID

from .handlers import files, common

ROUTES = [
    web.get("/echo/", common.echo),
    web.post("/files/", files.upload),
    web.get("/files/{id}/", files.get),
    web.delete("/files/{id}/", files.delete),
    web.get("/files/{id}/download/", files.download),
]

def make_download_url(link_id: UUID) -> str:
    return f"/download/{link_id}"
