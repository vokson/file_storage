import os
from datetime import datetime, timedelta
from logging import config as logging_config

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.logger import LOGGING

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(BASE_DIR, "..")

logging_config.dictConfig(LOGGING)


class DatabaseSettings(BaseModel):
    host: str
    port: int
    user: str
    password: str
    dbname: str


class BrokerSettings(BaseSettings):
    host: str
    port: int
    user: str
    password: str
    vhost: str
    exchange: str
    queue: str
    publish_retry_count: int


class Settings(BaseSettings):
    app_name: str
    server: str
    other_servers: list[str]
    db: DatabaseSettings
    broker: BrokerSettings
    storage_path: str = Field("/storage")
    storage_time_for_links: int = Field(3600)
    accounts_table: str = Field("accounts")
    files_table: str = Field("files")
    links_table: str = Field("links")
    broker_messages_table: str = Field("broker_messages")

    model_config = SettingsConfigDict(
        extra="allow",
        #  Для локальной разработки вне docker
        env_file=(
            os.path.join(ENV_DIR, ".env"),
            os.path.join(ENV_DIR, ".env.dev"),
        ),
        env_nested_delimiter="__",
    )


settings = Settings()


def tz_now(seconds: int = 0):
    # Moscow time on server
    return datetime.now() + timedelta(seconds=seconds)


db_dsl = {
    "host": settings.db.host,
    "port": settings.db.port,
    "user": settings.db.user,
    "database": settings.db.dbname,
    "password": settings.db.password,
}

broker_url = (
    f"amqp://{settings.broker.user}:"
    f"{settings.broker.password}@{settings.broker.host}:"
    f"{settings.broker.port}/{settings.broker.vhost}"
)
