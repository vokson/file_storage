import os
from datetime import datetime, timedelta
from logging import config as logging_config

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.logger import LOGGING

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(BASE_DIR, "..")

logging_config.dictConfig(LOGGING)

# class DatabaseTableSettings(BaseModel):
#     accounts: str = Field('accounts')
#     files: str = Field('files')


class DatabaseSettings(BaseModel):
    host: str
    port: int
    user: str
    password: str
    dbname: str


# class RabbitQueueSettings(BaseSettings):
#     listen_s3_events: str
#     file_operations: str


# class RabbitSettings(BaseSettings):
#     host: str
#     port: int
#     user: str
#     password: str
#     vhost: str
#     exchange: str
#     queues: RabbitQueueSettings



class Settings(BaseSettings):
    server: str
    db: DatabaseSettings
    # rabbitmq: RabbitSettings
    storage_path: str = Field("/storage")
    storage_time_for_links: int = Field(3600)
    accounts_table: str = Field("accounts")
    files_table: str = Field("files")
    links_table: str = Field("links")

    model_config = SettingsConfigDict(
        extra="allow",
        #  Для локальной разработки вне docker
        env_file=(
            os.path.join(ENV_DIR, ".env"),
            os.path.join(ENV_DIR, ".env.dev"),
        ),
        env_nested_delimiter="__",
    )

    # class Config:
    #     extra = "allow"
    #     #  Для локальной разработки вне docker
    #     env_file = (
    #         os.path.join(ENV_DIR, ".env"),
    #         os.path.join(ENV_DIR, ".env.dev"),
    #     )
    #     env_nested_delimiter = "__"


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

# rabbitmq_url = (
#     f"amqp://{settings.rabbitmq.user}:"
#     f"{settings.rabbitmq.password}@{settings.rabbitmq.host}:"
#     f"{settings.rabbitmq.port}/{settings.rabbitmq.vhost}"
# )

# rabbit_args = (rabbitmq_url, settings.rabbitmq.exchange)
