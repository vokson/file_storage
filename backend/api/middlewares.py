import logging
from functools import wraps
from typing import Awaitable, Callable, Type
from uuid import UUID

from aiohttp import web
from pydantic import BaseModel, ValidationError

from backend.api.dependables import get_bus
from backend.api.transformers import transform_exception
from backend.core import exceptions
from backend.domain import commands

logger = logging.getLogger(__name__)


@web.middleware
async def error_middleware(request, handler):
    try:
        if request.match_info.http_exception is not None:
            raise request.match_info.http_exception

        return await handler(request)

    except Exception as e:
        return transform_exception(e)


def verify_auth_token():
    def wrapper(f: Callable) -> Callable:
        @wraps(f)
        async def inner(request: web.Request, *args, **kwargs) -> Awaitable:
            try:
                auth_token = UUID(request.headers.getone("Authorization", ""))
            except ValueError:
                raise exceptions.AuthTokenFail

            bus = await get_bus()
            cmd = commands.GetAccountNameByAuthToken(auth_token=auth_token)
            account_name = await bus.handle(cmd)
            if account_name is None:
                raise exceptions.AuthTokenFail

            return await f(
                request, *args, _account_name=account_name, **kwargs
            )

        return inner

    return wrapper


def validate_path_parameters(model: Type[BaseModel]):
    def wrapper(f: Callable) -> Callable:
        @wraps(f)
        async def inner(request: web.Request, *args, **kwargs) -> Awaitable:
            try:
                params = model(**request.match_info)
            except ValidationError:
                raise exceptions.ParameterPathWrong

            return await f(
                request, *args, _path_parameters=dict(params), **kwargs
            )

        return inner

    return wrapper


def validate_json_body(model: Type[BaseModel]):
    def wrapper(f: Callable) -> Callable:
        @wraps(f)
        async def inner(request: web.Request, *args, **kwargs) -> Awaitable:
            if not request.has_body or not request.can_read_body:
                raise exceptions.ParameterBodyWrong

            if request.content_type != "application/json":
                raise exceptions.RequestBodyNotJson

            try:
                data = await request.json()
                obj = model(**data)
            except ValidationError as e:
                logger.info(e)
                raise exceptions.ParameterBodyWrong

            return await f(request, *args, _body=obj, **kwargs)

        return inner

    return wrapper


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

            try:
                reader = await request.multipart()
                field = await reader.next()

            except Exception as e:
                logger.info(e)
                raise exceptions.ParameterBodyWrong

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
