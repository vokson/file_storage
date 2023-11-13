from pydantic.dataclasses import dataclass as pydantic_dataclass
from backend.domain.models import File


class Event:
    pass


# ***** FILE *****


@pydantic_dataclass
class FileDeleted(Event):
    file: File

@pydantic_dataclass
class FileStored(Event):
    file: File