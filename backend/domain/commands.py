from pydantic import UUID4, BaseModel
from typing import AsyncGenerator, Callable, Awaitable
from dataclasses import dataclass
from pydantic.dataclasses import dataclass as pydantic_dataclass


class Command:
    pass

@pydantic_dataclass
class GetAccountIdByAuthToken(Command):
    auth_token: UUID4

@pydantic_dataclass
class GetFile(Command):
    account_id: UUID4
    file_id: UUID4

@pydantic_dataclass
class DownloadFile(Command):
    account_id: UUID4
    file_id: UUID4

@dataclass
class UploadFile(Command):
    account_id: UUID4
    filename: str
    get_coro_with_bytes_func: Callable[[int], Awaitable[bytearray]]
