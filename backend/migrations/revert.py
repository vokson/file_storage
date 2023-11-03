import asyncio
import logging
import os
import argparse
import sys
from os import walk

import asyncpg
from asyncpg.exceptions import UndefinedTableError

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
SQL_DIR = os.path.join(CURRENT_DIR, "sql", "reverse")

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
                "DELETE FROM __migrations__ WHERE name = $1;",
                filename,
            )
            logger.info(f"Reverse {filename} - OK")

        except Exception as e:
            logger.error(e)
            logger.info(f"Reverse {filename} - FAIL")


def get_filenames(path):
    return next(walk(path), (None, None, []))[2]

def get_count() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--count', type=int, default=1)
    args = parser.parse_args()
    return args.count


async def main():
    count = get_count()
    if count <=0:
        logger.info("Count of migrations to be reversed must be > 0")
        return

    conn = await asyncpg.connect(**db_dsl)

    migrations = await get_migrations(conn)

    #  Создаем таблицу __migrations__
    if migrations is None:
        logger.info("No migrations !!")
        return

    #  Анализируем записи в __migrations__ и файлы на диске
    migrations = {x["name"] for x in await get_migrations(conn)}

    #  Применяем миграции
    for filename in sorted(migrations, reverse=True):
        await apply_migration(conn, SQL_DIR, filename)

        count -= 1
        if count == 0:
            break

    await conn.close()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())

    except KeyboardInterrupt:
        pass
