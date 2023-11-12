import json
import logging

import aiohttp
import pytest_asyncio

from backend.service_layer.handlers.command.dependables import COMMAND_HANDLERS
from backend.service_layer.handlers.event.dependables import EVENT_HANDLERS
from backend.service_layer.message_bus import MessageBus
from backend.service_layer.uow import UnitOfWork

logger = logging.Logger(__name__)


# @pytest_asyncio.fixture()
# async def bus(
#     pool, file_storage, account_repository, file_repository, link_repository
# ):
#     bootstrap = [
#         "db",
#         "account_repository",
#         "file_repository",
#         "link_repository",
#     ]

#     async def get_account_repository():
#         return account_repository

#     async def get_file_storage():
#         return file_storage

#     async def get_file_repository():
#         return file_repository

#     async def get_link_repository():
#         return link_repository

#     async def get_db_conn():
#         conn = await pool.acquire()
#         await conn.set_type_codec(
#             "jsonb",
#             encoder=lambda x: x.json(),
#             decoder=json.loads,
#             schema="pg_catalog",
#         )
#         return conn

#     async def release_db_conn(conn):
#         await pool.release(conn)

#     unit_of_work = UnitOfWork(
#         bootstrap,
#         get_account_repository=get_account_repository,
#         get_file_repository=get_file_repository,
#         get_link_repository=get_link_repository,
#         get_file_storage=get_file_storage,
#         get_db_conn=get_db_conn,
#         release_db_conn=release_db_conn,
#     )

#     return MessageBus(unit_of_work, EVENT_HANDLERS, COMMAND_HANDLERS)


@pytest_asyncio.fixture()
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()