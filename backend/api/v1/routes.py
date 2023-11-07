from aiohttp import web
from uuid import UUID

from .handlers import files, common
from backend.core.config import settings

ROUTES = [
    web.get("/echo/", common.echo),

    web.post("/files/", files.post),
    web.get("/files/{file_id}/", files.get),
    web.delete("/files/{file_id}/", files.delete),

    web.get("/download/{link_id}/", files.download),
    web.post("/upload/{link_id}/", files.upload),
]

def _make_link_url(link_id: UUID, direction: str) -> str:
    return f"{settings.server}/{direction}/{link_id}/"

def make_download_url(link_id: UUID) -> str:
    return _make_link_url(link_id, 'download')

def make_upload_url(link_id: UUID) -> str:
    return _make_link_url(link_id, 'upload')
