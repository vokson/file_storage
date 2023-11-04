from abc import ABC, abstractmethod
from typing import Awaitable, Callable

from backend.adapters.file_storage.abstract import AbstractFileStorage
from backend.adapters.file_storage.local import get_local_file_storage

from backend.adapters.file_repository.abstract import AbstractFileRepository
from backend.adapters.file_repository.db import get_db_file_repository

from backend.adapters.account_repository.abstract import AbstractAccountRepository
from backend.adapters.account_repository.db import get_db_account_repository

# from src.adapters.broker import init_publisher
# from src.adapters.cache import init_cache
from backend.adapters.db import get_db_conn, release_db_conn

# from src.adapters.geoip import init_geo_ip
# from src.adapters.repositories.cdn_server import CdnServerRepository
# from src.adapters.repositories.file import FileRepository
# from src.adapters.repositories.file_share_links import FileShareLinkRepository
# from src.adapters.repositories.history import HistoryRepository
# from src.adapters.s3 import init_s3_pool
# from src.core.config import (cache_dsl, db_dsl, get_s3_dsl, rabbit_args,
#                              settings)

from backend.core.config import db_dsl


def get_db_connection():
    return get_db_conn(**db_dsl)


def release_db_connection(conn):
    return release_db_conn(conn)


# def get_cache_connection():
#     return init_cache(**cache_dsl)


# def get_s3_pool():
#     return init_s3_pool(settings.s3.bucket, get_s3_dsl)


# def get_publisher():
#     return init_publisher(*rabbit_args)


class AbstractUnitOfWork(ABC):
    def __init__(self):
        self._messages = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError

    def push_message(self, message):
        self._messages.append(message)

    def collect_new_messages(self):
        messages = self._messages[:]
        self._messages = []
        return messages


class UnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        bootstrap: list[str],
        get_file_storage: Callable[[], Awaitable[AbstractFileStorage]] | None = None,
        get_file_repository: Callable[..., Awaitable[AbstractFileRepository]]
        | None = None,
        get_account_repository: Callable[..., Awaitable[AbstractAccountRepository]]
        | None = None,
        get_db_conn: Callable[..., Awaitable] | None = None,
        release_db_conn: Callable[..., Awaitable] | None = None,
        # release_db_conn=release_db_conn,
        # get_cache=get_cache_connection,
        # get_geo_ip=init_geo_ip,
        # get_s3_pool=get_s3_pool,
        # get_publisher=get_publisher,
    ):
        super().__init__()
        self._bootstrap = bootstrap
        self._conn = None
        self._get_file_storage = get_file_storage or get_local_file_storage
        self._get_file_repository = get_file_repository or get_db_file_repository
        self._get_account_repository = (
            get_account_repository or get_db_account_repository
        )
        self._get_db_conn = get_db_conn or get_db_connection
        self._release_db_conn = release_db_conn or release_db_connection
        # self._get_cache_conn = get_cache
        # self._get_s3_pool = get_s3_pool
        # self._get_geo_ip = get_geo_ip
        # self._get_publisher = get_publisher

    async def startup(self):
        if "file_repository" in self._bootstrap:
            self._file_storage = await self._get_file_storage()

    #     if "cache" in self._bootstrap:
    #         self.cache = await self._get_cache_conn()

    #     if "s3" in self._bootstrap:
    #         self.s3_pool = await self._get_s3_pool()

    #     if "geoip" in self._bootstrap:
    #         self.geoip = await self._get_geo_ip()

    #     if "publisher" in self._bootstrap:
    #         self.publisher = await self._get_publisher()

    async def __aenter__(self):
        if "db" in self._bootstrap:
            self._is_done = False
            self._conn = await self._get_db_conn()
            self._transaction = self._conn.transaction()
            await self._transaction.start()

            if "account_repository" in self._bootstrap:
                self.account_repository = await self._get_account_repository(self._conn)

            if "file_repository" in self._bootstrap:
                self.file_repository = await self._get_file_repository(
                    self._file_storage, self._conn
                )

        return self

    async def __aexit__(self, *args):
        if not self._is_done:
            await super().__aexit__()

        if "db" in self._bootstrap:
            if not self._is_done:
                await super().__aexit__()

            await self._release_db_conn(self._conn)

    async def commit(self):
        self._is_done = True
        if "db" in self._bootstrap:
            self._is_done = True
            await self._transaction.commit()

    async def rollback(self):
        self._is_done = True
        if "db" in self._bootstrap:
            self._is_done = True
            await self._transaction.rollback()
