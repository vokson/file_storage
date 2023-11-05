from functools import wraps
from typing import Awaitable, Callable, Type
from uuid import UUID

from aiohttp import web
from pydantic import BaseModel, ValidationError

from backend.api.transformers import transform_exception
from backend.api.dependables import get_bus
from backend.core import exceptions
from backend.domain import commands
from backend.service_layer.message_bus import MessageBus


@web.middleware
async def error_middleware(request, handler):
    try:
        if request.match_info.http_exception is not None:
            raise request.match_info.http_exception

        return await handler(request)

    except Exception as e:
        return transform_exception(e)


@web.middleware
async def verify_auth_token(request, handler):
    try:
        auth_token = UUID(request.headers.getone("Authorization", ""))
    except ValueError:
        raise exceptions.AuthTokenFail

    bus = await get_bus()
    cmd = commands.GetAccountIdByAuthToken(auth_token=auth_token)
    account_id = await bus.handle(cmd)
    if account_id is None:
        raise exceptions.AuthTokenFail

    return await handler(request,  _account_id=account_id)


def validate_path_parameters(model: Type[BaseModel]):
    def wrapper(f: Callable) -> Callable:
        @wraps(f)
        async def inner(request: web.Request, *args, **kwargs) -> Awaitable:
            try:
                params = model(**request.match_info)
            except ValidationError:
                raise exceptions.ParameterPathWrong

            return await f(request, *args, path_parameters=dict(params), **kwargs)

        return inner

    return wrapper
