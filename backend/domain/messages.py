from typing import Any

from pydantic import model_serializer, Field
from pydantic.dataclasses import dataclass as pydantic_dataclass
from abc import abstractmethod

from backend.domain import models


@pydantic_dataclass
class Message:
    key: str

    @property
    @abstractmethod
    def to_broker(self) -> dict[str, Any]:
        pass


@pydantic_dataclass
class FileMessage(Message):
    file: models.File

    @property
    def to_broker(self) -> dict[str, Any]:
        return dict(self.file.to_broker())


@pydantic_dataclass
class FileStored(FileMessage):
    key: str = Field("FILE.STORED")

@pydantic_dataclass
class FileDeleted(FileMessage):
    key: str = Field("FILE.DELETED")
