from pydantic import UUID4, BaseModel


class Request(BaseModel):
    pass


class IdUUIDMixin(BaseModel):
    id: UUID4
