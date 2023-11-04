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
        return await handler(request)

    except Exception as e:
        return transform_exception(e)


@web.middleware
async def verify_auth_token(request, handler):
    try:
        print(request.headers)
        
        auth_token = UUID(request.headers.getone("Authorization", ""))
    except ValueError:
        raise exceptions.AuthTokenFail

    print(auth_token)

    bus = await get_bus()
    cmd = commands.GetAccountIdByAuthToken(auth_token=auth_token)
    account_id = await bus.handle(cmd)
    if account_id is None:
        raise exceptions.AuthTokenFail

    return await handler(request,  _account_id=account_id)


# def verify_auth_token(request, handler):
#     def wrapper(f: Callable) -> Callable:
#         @wraps(f)
#         async def inner(
#             request: web.Request, *args, bus: MessageBus | None = None, **kwargs
#         ) -> Awaitable:
#             auth_token = request.headers.getone("Authorization", None)
#             if auth_token is None:
#                 raise exceptions.AuthTokenFail

#             bus = bus or await get_bus()
#             cmd = commands.GetAccountIdByAuthToken(auth_token=UUID(auth_token))
#             account_id = await bus.handle(cmd)
#             if account_id is None:
#                 raise exceptions.AuthTokenFail

#             return await f(request, *args, _account_id=account_id, **kwargs)

#         return inner

    return wrapper

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
