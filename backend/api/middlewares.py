from functools import wraps
from typing import Awaitable, Callable, Type

from aiohttp import web
from pydantic import BaseModel, ValidationError

from backend.api.transformers import transform_exception
from backend.core import exceptions


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)

    except Exception as e:
        return transform_exception(e)


def validate_path_parameters(model: Type[BaseModel]):
    def wrapper(f: Callable) -> Callable:
        @wraps(f)
        async def inner(request: web.Request, *args, **kwargs) -> Awaitable:
            try:
                params = model(**request.match_info)
            except ValidationError:
                raise exceptions.ParameterPathWrong

            return await f(request, *args, **kwargs, path_parameters=dict(params))

        return inner

    return wrapper
