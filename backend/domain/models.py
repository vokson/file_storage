from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field, field_validator, model_serializer

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


def greater_than_zero(cls, v: int) -> int:
    if v <= 0:
        raise ValueError("must be greater than zero")
    return v


def greater_than_zero_or_equal(cls, v: int) -> int:
    if v < 0:
        raise ValueError("must be greater than zero or equal")
    return v


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
    has_stored: bool = False
    stored: datetime | None = None
    has_deleted: bool = False
    deleted: datetime | None = None
    has_erased: bool = False
    erased: datetime | None = None

    size_greater_than_zero_or_equal = field_validator("size")(
        greater_than_zero_or_equal
    )

    def to_broker(self) -> dict[str, Any]:
        return self.model_dump(
            include={"id", "account_id", "name", "size", "stored", "deleted"}
        )


class Link(AbstractModel, IdMixin, CreatedMixin):
    file_id: UUID4
    type: str = Field(pattern=r"^D|U$")
    expired: datetime


class BrokerMessage(AbstractModel, IdMixin, CreatedMixin):
    app: str
    key: str
    body: dict
    direction: str = Field(pattern=r"^I|O$")
    has_executed: bool = False
    updated: datetime = Field(default_factory=tz_now)
    has_execution_stopped: bool = False
    count_of_retries: int = 0
    next_retry_at: datetime
    seconds_to_next_retry: int = 1

    count_of_retries_greater_than_zero_or_equal = field_validator(
        "count_of_retries"
    )(greater_than_zero_or_equal)

    seconds_to_next_retry_greater_than_zero = field_validator(
        "seconds_to_next_retry"
    )(greater_than_zero)
