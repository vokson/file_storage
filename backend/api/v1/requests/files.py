from .abstract import IdUUIDMixin, Request


class DownloadRequest(Request, IdUUIDMixin):
    pass
