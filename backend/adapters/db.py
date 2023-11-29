import json
import logging

import asyncpg
from asyncpg import Pool

from backend.tools.decorators import backoff

logger = logging.getLogger(__name__)
pool: Pool | None = None


@backoff()
async def create_pool(**dsl):
    return await asyncpg.create_pool(**dsl)


async def init_db(**dsl):
    global pool
    if not pool:
        logger.info("Creating DB pool ..")
        pool = await create_pool(**dsl)
        logger.info(f"DB pool {id(pool)} has been created")
    return pool


async def get_db_conn(**dsl):
    pool = await init_db(**dsl)
    conn = await pool.acquire()

    await conn.set_type_codec(
        "jsonb",
        encoder=lambda x: json.dumps(x, default=str),
        decoder=json.loads,
        schema="pg_catalog",
    )

    logger.debug(
        f"DB connection {id(conn)} for pool {id(pool)} has been acquired",
    )
    return conn


async def release_db_conn(conn):
    logger.debug(
        f"Releasing DB connection {id(conn)} for pool {id(pool)} ... ",
    )
    await pool.release(conn)
    logger.debug("DB connection has been created")


async def close_db():
    global pool
    if pool:
        logger.info(f"Closing DB pool {id(pool)} ... ")
        await pool.close()
        logger.info("DB pool has been closed")
