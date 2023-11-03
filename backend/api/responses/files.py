from datetime import datetime
from pydantic import UUID4
from .abstract import Response


class FileReponse(Response):
    id: UUID4
    name: str
    size: int
    key: UUID4
    created: datetime
