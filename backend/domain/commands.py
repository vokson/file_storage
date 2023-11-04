from pydantic import UUID4, BaseModel


class Command(BaseModel):
    pass

class GetAccountIdByAuthToken(Command):
    auth_token: UUID4

class GetFile(Command):
    account_id: UUID4
    file_id: UUID4

class DownloadFile(Command):
    account_id: UUID4
    file_id: UUID4
