from functools import wraps
from typing import Awaitable, Callable, Type
from uuid import UUID

from aiohttp import web
from pydantic import BaseModel, ValidationError

from backend.api.transformers import transform_exception
from backend.api.dependables import get_bus
from backend.core import exceptions
from backend.domain import commands


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

    return await handler(request, _account_id=account_id)


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


# def validate_json_body(model: Type[BaseModel]):
#     def wrapper(f: Callable) -> Callable:
#         @wraps(f)
#         async def inner(request: web.Request, *args, **kwargs) -> Awaitable:
#             if not request.has_body or not request.can_read_body:
#                 raise exceptions.ParameterBodyWrong

#             if request.content_type != "application/json":
#                 raise exceptions.RequestBodyNotJson

#             try:
#                 model(**await request.json())
#             except ValidationError:
#                 raise exceptions.ParameterBodyWrong

#             return await f(request, *args, **kwargs)

#         return inner

#     return wrapper


def validate_file_body():
    def wrapper(f: Callable) -> Callable:
        @wraps(f)
        async def inner(request: web.Request, *args, **kwargs) -> Awaitable:
            if not (
                request.has_body
                or request.can_read_body
                or request.content_type != "multipart/form-data"
            ):
                raise exceptions.ParameterBodyWrong

            reader = await request.multipart()
            field = await reader.next()

            if field.name != "file":
                raise exceptions.ParameterBodyWrong

            return await f(
                request,
                *args,
                _filename=field.filename,
                _file=field.read_chunk,
                **kwargs
            )

        return inner

    return wrapper
