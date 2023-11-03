import argparse
import asyncio
import logging
import os
import sys
from os import walk

import asyncpg
from asyncpg import Connection
from asyncpg.exceptions import UndefinedTableError

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
SQL_DIR_FORWARD = os.path.join(CURRENT_DIR, "sql", "forward")
SQL_DIR_REVERSE = os.path.join(CURRENT_DIR, "sql", "reverse")

sys.path.append(BASE_DIR)

from backend.core.config import db_dsl

logger = logging.getLogger(__name__)


async def get_migrations(conn: Connection) -> list:
    try:
        return await conn.fetch("SELECT * FROM __migrations__;")

    except UndefinedTableError:
        logger.info("Creating __migrations__ table.")
        await create_migrations(conn)
        logger.warning("__migrations__ table has been created.")
        return []


async def create_migrations(conn: Connection):
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


async def apply_migration(conn: Connection, path: str, filename: str, is_new: bool):
    migration_query = (
        """
        INSERT INTO __migrations__ (name, created)
        VALUES ($1, CURRENT_TIMESTAMP);
        """
        if is_new
        else "DELETE FROM __migrations__ WHERE name = $1;"
    )

    with open(os.path.join(path, filename)) as f:
        query = f.read()

        try:
            await conn.execute(query)
            await conn.execute(migration_query, filename)
            logger.info(f"{filename} - OK")

        except Exception as e:
            logger.error(e)
            logger.info(f"{filename} - FAIL")


def get_filenames(path):
    return next(walk(path), (None, None, []))[2]


def get_args() -> tuple[bool, int]:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--count", type=int, default=1)
    parser.add_argument("-r", "--reverse", action="store_true")
    args = parser.parse_args()
    return args.reverse, args.count


async def forward(conn: Connection, migrations: set[str]):
    #  Анализируем записи в __migrations__ и файлы на диске
    filenames = set(get_filenames(SQL_DIR_FORWARD))
    not_applied_migrations = filenames - migrations

    #  Применяем миграции
    if len(not_applied_migrations) == 0:
        logger.info("Nothing to migrate.")
        return

    for filename in sorted(not_applied_migrations):
        await apply_migration(conn, SQL_DIR_FORWARD, filename, True)


async def revert(conn: Connection, migrations: set[str], count: int):
    if len(migrations) == 0:
        logger.info("No migrations !!")
        return

    #  Применяем миграции
    logger.info(f"Reversing {count} migrations..")
    for filename in sorted(migrations, reverse=True):
        await apply_migration(conn, SQL_DIR_REVERSE, filename, False)

        count -= 1
        if count == 0:
            break


async def main():
    reverse, count = get_args()
    if reverse and count <= 0:
        logger.info("Count of migrations to be reversed must be > 0")
        return

    conn = await asyncpg.connect(**db_dsl)
    migrations = {x["name"] for x in await get_migrations(conn)}

    if reverse:
        await revert(conn, migrations, count)
    else:
        await forward(conn, migrations)

    await conn.close()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())

    except KeyboardInterrupt:
        pass
