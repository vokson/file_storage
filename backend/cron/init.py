from backend.service_layer.uow import (close_db_pool, close_http_session,
                                       init_db_pool, init_http_session)


async def startup():
    await init_db_pool()
    await init_http_session()


async def cleanup():
    await close_db_pool()
    await close_http_session()
