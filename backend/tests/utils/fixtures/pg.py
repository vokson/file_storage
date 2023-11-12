import json
import logging

import asyncpg
import pytest_asyncio

from backend.adapters.account_repository.db import DatabaseAccountRepository
from backend.adapters.file_repository.db import DatabaseFileRepository
from backend.adapters.link_repository.db import DatabaseLinkRepository
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
async def rollback_pg(pg_pool):
    conn = await pg_pool.acquire()

    await conn.set_type_codec(
        "jsonb",
        encoder=lambda x: x.json(),
        decoder=json.loads,
        schema="pg_catalog",
    )

    tr = conn.transaction()
    await tr.start()

    yield conn

    await tr.rollback()
    await pg_pool.release(conn)


@pytest_asyncio.fixture()
async def pg(pg_pool):
    conn = await pg_pool.acquire()

    await conn.set_type_codec(
        "jsonb",
        encoder=lambda x: x.json(),
        decoder=json.loads,
        schema="pg_catalog",
    )

    yield conn

    await pg_pool.release(conn)


@pytest_asyncio.fixture()
async def account_repository(pg):
    return DatabaseAccountRepository(pg)


@pytest_asyncio.fixture()
async def file_repository(pg, file_storage):
    return DatabaseFileRepository(file_storage, pg)


@pytest_asyncio.fixture()
async def link_repository(pg):
    return DatabaseLinkRepository(pg)


@pytest_asyncio.fixture()
async def rollback_account_repository(rollback_pg):
    return DatabaseAccountRepository(rollback_pg)


@pytest_asyncio.fixture()
async def rollback_file_repository(rollback_pg, file_storage):
    return DatabaseFileRepository(file_storage, rollback_pg)


@pytest_asyncio.fixture()
async def rollback_link_repository(rollback_pg):
    return DatabaseLinkRepository(rollback_pg)
