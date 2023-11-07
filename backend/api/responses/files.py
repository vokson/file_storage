from datetime import datetime
from pydantic import UUID4
from .abstract import Response


class FileResponse(Response):
    id: UUID4
    name: str
    size: int
    created: datetime

class FileResponseWithLink(FileResponse):
    link: str
