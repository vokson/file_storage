from .abstract import IdUUIDMixin, Request


class GetRequest(Request, IdUUIDMixin):
    pass

class DownloadRequest(GetRequest):
    pass
