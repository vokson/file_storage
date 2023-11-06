from pydantic import UUID4
from uuid import UUID
from typing import Callable, Awaitable
from dataclasses import dataclass
from pydantic.dataclasses import dataclass as pydantic_dataclass


class Command:
    pass

@pydantic_dataclass
class GetAccountIdByAuthToken(Command):
    auth_token: UUID4

@dataclass
class GetFile(Command):
    account_id: UUID
    file_id: UUID
    make_download_url: Callable[[UUID], str]

class DownloadFile(GetFile):
    pass

@dataclass
class UploadFile(Command):
    account_id: UUID4
    filename: str
    get_coro_with_bytes_func: Callable[[int], Awaitable[bytearray]]

class DeleteFile(GetFile):
    pass

@pydantic_dataclass
class EraseFile(GetFile):
    file_id: UUID4

# @dataclass
# class AddLink(Command):
#     file_id: UUID4
#     expire_time_in_sec: int