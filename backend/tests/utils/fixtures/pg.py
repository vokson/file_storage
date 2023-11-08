import logging

import asyncpg
import pytest_asyncio

from backend.adapters.account_repository.db import DatabaseAccountRepository
from backend.adapters.file_repository.db import DatabaseFileRepository
from backend.core.config import db_dsl
from backend.tools.decorators import backoff

logger = logging.Logger(__name__)


@backoff()
@pytest_asyncio.fixture(scope="session")
async def pg_pool():
    pool = await asyncpg.create_pool(**db_dsl)
    yield pool

    if pool:
        await pool.close()


@pytest_asyncio.fixture()
async def pg(pg_pool):
    conn = await pg_pool.acquire()
    tr = conn.transaction()
    await tr.start()

    yield conn

    await tr.rollback()
    await pg_pool.release(conn)


@pytest_asyncio.fixture()
async def account_repository(pg):
    rep = DatabaseAccountRepository(pg)
    yield rep


@pytest_asyncio.fixture()
async def file_repository(pg, file_storage):
    rep = DatabaseFileRepository(file_storage, pg)
    yield rep
