from .abstract import IdUUIDMixin, Request


class GetRequestPath(Request, IdUUIDMixin):
    pass


class DownloadRequestPath(GetRequestPath):
    pass


class DeleteRequestPath(GetRequestPath):
    pass
