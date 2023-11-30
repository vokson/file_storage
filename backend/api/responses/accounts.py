from .abstract import Response


class AccountResponse(Response):
    name: str
    actual_size: int
    total_size: int
    is_active: bool
