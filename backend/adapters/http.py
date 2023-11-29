import logging

import aiohttp

logger = logging.getLogger(__name__)

session: aiohttp.ClientSession | None = None


async def init_http():
    global session
    if not session:
        logger.info("Creating HTTP session ..")
        session = aiohttp.ClientSession()
        logger.info(f"HTTP session {id(session)} has been created")

    return session


async def get_http():
    session = await init_http()

    logger.debug(
        f"HTTP session {id(session)} has been acquired",
    )
    return session


async def close_http():
    global session
    if session:
        logger.info(f"Closing HTTP session {id(session)} ... ")
        await session.close()
        logger.info("HTTP session has been closed")
