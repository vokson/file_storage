from uuid import UUID

from aiohttp import web

from backend.core.config import settings

from .handlers import files

ROUTES = [
    web.post("/files/", files.post),
    web.get("/files/{file_id}/", files.get),
    web.delete("/files/{file_id}/", files.delete),

    web.get("/download/{link_id}/", files.download),
    web.post("/upload/{link_id}/", files.upload),
]

def make_files_url(host: str | None = None) -> str:
    return f"{host if host else settings.server}/files/"

def make_file_url(file_id: UUID, host: str | None = None) -> str:
    return f"{make_files_url(host=host)}{file_id}/"

def _make_link_url(link_id: UUID, direction: str) -> str:
    return f"{settings.server}/{direction}/{link_id}/"

def make_download_url(link_id: UUID) -> str:
    return _make_link_url(link_id, 'download')

def make_upload_url(link_id: UUID) -> str:
    return _make_link_url(link_id, 'upload')
