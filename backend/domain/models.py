from uuid import uuid4
from datetime import datetime
from pydantic import UUID4, BaseModel, Field, field_validator
from backend.core.config import tz_now


class AbstractModel(BaseModel):
    class Config:
        json_encoders = {datetime: lambda x: str(x)}


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
    key: UUID4
    account_id: UUID4
    has_deleted: bool = Field(False)
    deleted: datetime | None = Field(None)
    has_erased: bool = Field(False)
    erased: datetime | None = Field(None)

    @field_validator("size")
    @classmethod
    def greater_than_zero(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("must be grater than zero")
        return v


# class FileShareLink(AbstractIdModel, CreatedMixin):
#     file_id: UUID
#     password: str | None
#     expire_at: datetime | None


# class UserAction(AbstractIdModel, CreatedMixin):
#     user_id: UUID
#     obj_id: UUID
#     data: dict
#     event: str


# class FileActionData(BaseModel):
#     name: str


# class FileRenameActionData(BaseModel):
#     old_name: str
#     new_name: str


# class FileUserAction(UserAction):
#     data: FileActionData
