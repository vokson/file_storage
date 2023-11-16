from dataclasses import dataclass
from typing import Awaitable, Callable
from uuid import UUID

from pydantic import UUID4
from pydantic.dataclasses import dataclass as pydantic_dataclass

from backend.domain.messages import Message
from backend.domain.models import BrokerMessage


class Command:
    pass


# ***** FILE *****


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
class CloneFile(Command):
    account_id: UUID
    file_id: UUID
    name: str
    size: int



@pydantic_dataclass
class EraseFile(GetFile):
    file_id: UUID4


# ***** EVENT LOOP *****


@pydantic_dataclass
class GetBrokerMessages(Command):
    chunk_size: int


class GetMessagesToBeSendToBroker(GetBrokerMessages):
    pass


class GetMessagesReceivedFromBroker(GetBrokerMessages):
    pass


@pydantic_dataclass
class AddOutgoingBrokerMessage(Command):
    message: Message
    delay: int = 0


@pydantic_dataclass
class AddIncomingBrokerMessage(Command):
    id: UUID
    app: str
    key: str
    body: dict


@pydantic_dataclass
class MarkBrokerMessageAsExecuted(Command):
    ids: list[UUID]


@pydantic_dataclass
class ScheduleNextRetryForBrokerMessage(Command):
    ids: list[UUID]


@pydantic_dataclass
class PublishMessageToBroker(Command):
    message: BrokerMessage


@pydantic_dataclass
class ConsumeMessageFromBroker(Command):
    id: str
    app: str
    key: str
    body: str


@pydantic_dataclass
class ExecuteBrokerMessage(Command):
    message: BrokerMessage