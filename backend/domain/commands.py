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


@dataclass
class AddFile(Command):
    account_id: UUID
    make_upload_url: Callable[[UUID], str]


@pydantic_dataclass
class DownloadFile(Command):
    link_id: UUID


@dataclass
class UploadFile(Command):
    link_id: UUID
    filename: str
    get_coro_with_bytes_func: Callable[[int], Awaitable[bytearray]]


@pydantic_dataclass
class DeleteFile(Command):
    account_id: UUID
    file_id: UUID


@pydantic_dataclass
class EraseFile(GetFile):
    file_id: UUID4
