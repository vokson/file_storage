from datetime import datetime

from pydantic import UUID4, Field

from backend.core.config import settings

from .abstract import Response


class FileResponse(Response):
    id: UUID4
    name: str
    size: int
    created: datetime
    stored: datetime | None
    deleted: datetime | None
    erased: datetime | None


class FileResponseWithLink(FileResponse):
    link: str
