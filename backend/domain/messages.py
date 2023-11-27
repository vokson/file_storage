from abc import abstractmethod
from typing import Any

from pydantic.dataclasses import dataclass as pydantic_dataclass

from backend.domain import models
from backend.core.config import settings


@pydantic_dataclass
class Message:
    @property
    @abstractmethod
    def to_broker(self) -> dict[str, Any]:
        pass


@pydantic_dataclass
class FileMessage(Message):
    file: models.File

    @property
    def to_broker(self) -> dict[str, Any]:
        return {**self.file.to_broker(), "server": settings.server_name}


@pydantic_dataclass
class FileStored(FileMessage):
    key: str = "FILE.STORED"

@pydantic_dataclass
class FileDeleted(FileMessage):
    key: str = "FILE.DELETED"
