from pydantic import UUID4, BaseModel


class Command(BaseModel):
    pass

class GetFile(Command):
    id: UUID4

class DownloadFile(Command):
    id: UUID4
