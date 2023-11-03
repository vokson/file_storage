import asyncio
import logging
import os
import sys
from os import walk

import asyncpg
from asyncpg.exceptions import UndefinedTableError

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
SQL_DIR = os.path.join(CURRENT_DIR, "sql", "forward")

sys.path.append(BASE_DIR)

from backend.core.config import db_dsl

logger = logging.getLogger(__name__)


async def get_migrations(conn):
    try:
        return await conn.fetch("SELECT * FROM __migrations__;")
    except UndefinedTableError:
        logger.warning("Table __migrations__ does not exist.")


async def create_migrations(conn):
    await conn.execute(
        """
        CREATE TABLE __migrations__
        (
            id serial primary key,
            name VARCHAR(250) not null,
            created TIMESTAMP
        );
        """,
    )


async def apply_migration(conn, path, filename):
    with open(os.path.join(path, filename)) as f:
        query = f.read()

        try:
            await conn.execute(query)
            await conn.execute(
                """
                INSERT INTO __migrations__ (name, created)
                VALUES ($1, CURRENT_TIMESTAMP);
                """,
                filename,
            )
            logger.info(f"{filename} - OK")

        except Exception as e:
            logger.error(e)
            logger.info(f"{filename} - FAIL")


def get_filenames(path):
    return next(walk(path), (None, None, []))[2]


async def main():

    conn = await asyncpg.connect(**db_dsl)

    migrations = await get_migrations(conn)

    #  Создаем таблицу __migrations__
    if migrations is None:
        logger.info("Creating __migrations__ table.")
        await create_migrations(conn)
        logger.warning("__migrations__ table has been created.")

    #  Анализируем записи в __migrations__ и файлы на диске
    migrations = {x["name"] for x in await get_migrations(conn)}
    filenames = set(get_filenames(SQL_DIR))

    not_applied_migrations = filenames - migrations

    #  Применяем миграции
    if len(not_applied_migrations) == 0:
        logger.info("Nothing to migrate.")

    else:
        for filename in sorted(not_applied_migrations):
            await apply_migration(conn, SQL_DIR, filename)

    await conn.close()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())

    except KeyboardInterrupt:
        pass