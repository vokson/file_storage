import asyncio
import logging
import os
import sys
import asyncpg
from pathlib import Path
import shutil

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(BASE_DIR)

from backend.core.config import settings, tz_now
from backend.core.config import db_dsl

logger = logging.getLogger()

ADD_QUERY = f"""
                INSERT INTO {settings.files_table}
                    (
                        account_name,
                        id,
                        stored_id,
                        name,
                        size,
                        tag,
                        created,
                        stored,
                        has_stored
                    )
                VALUES
                    ('DOCUMENTS', $1, $1, $2, $3, 'block-01', $4, $4, TRUE);
                """


async def main():
    conn = await asyncpg.connect(**db_dsl)

    error_count = 0
    with open(os.path.join(settings.storage_path, 'output.txt'), mode='r', encoding='utf-8') as f:
        for row in f:
            arr: list[str] = row.strip().split('|')
            id, name, size = tuple(arr)

            try:
                await conn.execute(
                    ADD_QUERY,
                    id,
                    name,
                    int(size),
                    tz_now(),
                )

            except Exception as e:
                logger.error(f"ERROR - {e}")
                error_count += 1
                continue

            src_path = os.path.join(settings.storage_path, id)

            dest_path = os.path.join(settings.storage_path, id[0:2])

            Path(dest_path).mkdir(parents=True, exist_ok=True)
            dest_path = os.path.join(dest_path, id)

            try:
                shutil.copyfile(src_path, dest_path)
                logger.info(f"COPIED - {id}")

            except FileNotFoundError:
                logger.error(f"ERROR - File {src_path} has not been found")
                error_count += 1
                continue
    

    await conn.close()

    logger.info('******************************')
    logger.info(f"COUNT OF ERRORS: {error_count}")



if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
