from datetime import datetime

from pydantic import UUID4

from .abstract import Response


class NotStoredFileResponse(Response):
    id: UUID4
    link: str
    created: datetime


class FileResponse(Response):
    id: UUID4
    name: str
    size: int
    stored: datetime

class FileResponseWithLink(FileResponse):
    link: str
