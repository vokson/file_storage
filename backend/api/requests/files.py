from pydantic import UUID4
from .abstract import Request


class GetRequestPath(Request):
    file_id: UUID4


class DownloadRequestPath(Request):
    link_id: UUID4


class UploadRequestPath(DownloadRequestPath):
    pass


class DeleteRequestPath(Request):
    file_id: UUID4
