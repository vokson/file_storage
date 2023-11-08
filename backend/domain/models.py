from datetime import datetime
from uuid import uuid4

from pydantic import (
    UUID4,
    BaseModel,
    Field,
    field_validator,
    model_serializer,
)
from typing import Any

from backend.core.config import tz_now


class AbstractModel(BaseModel):
    #  Не использовал json_encoders из-за Deprecated
    @model_serializer
    def datetime_to_str(self) -> dict[str, Any]:
        result = {}
        for key in [x for x in self.__dict__.keys() if not x.startswith("__")]:
            value = getattr(self, key)
            result[key] = str(value) if type(value) is datetime else value

        return result


class IdMixin(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)


class CreatedMixin(BaseModel):
    created: datetime = Field(default_factory=tz_now)


class Account(AbstractModel, IdMixin):
    name: str
    auth_token: UUID4
    is_active: bool


class File(AbstractModel, IdMixin, CreatedMixin):
    stored_id: UUID4
    name: str
    size: int
    account_id: UUID4
    has_stored: bool = Field(False)
    stored: datetime | None = Field(None)
    has_deleted: bool = Field(False)
    deleted: datetime | None = Field(None)
    has_erased: bool = Field(False)
    erased: datetime | None = Field(None)

    @field_validator("size")
    @classmethod
    def greater_than_zero(cls, v: int) -> int:
        if v < 0:
            raise ValueError("must be greater than zero or equal")
        return v


class Link(AbstractModel, IdMixin, CreatedMixin):
    file_id: UUID4
    type: str = Field(pattern=r"^D|U$")
    expired: datetime
