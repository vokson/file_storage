from pydantic import UUID4, BaseModel


class Command(BaseModel):
    pass

class DownloadFile(Command):
    id: UUID4
