import os
from logging import config as logging_config
from datetime import datetime, timedelta


from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
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
    # tables: DatabaseTableSettings


# class AuthServiceSettings(BaseSettings):
#     host: str
#     port: int


# class CacheSettings(BaseSettings):
#     host: str
#     port: int


# class S3Settings(BaseSettings):
#     user: str
#     password: str
#     bucket: str


# class GeoSettings(BaseSettings):
#     use_real_ip: bool


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
    # debug: bool
    # app_name: str
    # auth: AuthServiceSettings
    db: DatabaseSettings
    # cache: CacheSettings
    # s3: S3Settings
    # geo: GeoSettings
    # rabbitmq: RabbitSettings
    storage_path: str = Field("/storage")
    accounts_table: str = Field('accounts')
    files_table: str = Field('files')

    class Config:
        extra='allow'
        #  Для локальной разработки вне docker
        env_file = (
            os.path.join(ENV_DIR, ".env"),
            os.path.join(ENV_DIR, ".env.dev"),
        )
        env_nested_delimiter = "__"


settings = Settings()


def tz_now():
    return datetime.now()  # Moscow time on server
    # return datetime.now() + timedelta(hours=3)  # Moscow Time


db_dsl = {
    "host": settings.db.host,
    "port": settings.db.port,
    "user": settings.db.user,
    "database": settings.db.dbname,
    "password": settings.db.password,
}

# cache_dsl = {
#     "host": settings.cache.host,
#     "port": settings.cache.port,
# }


# def get_s3_dsl(host: str, port: int) -> dict:
#     return {
#         "endpoint": f"{host}:{port}",
#         "access_key": settings.s3.user,
#         "secret_key": settings.s3.password,
#         "secure": False,
#     }


# rabbitmq_url = (
#     f"amqp://{settings.rabbitmq.user}:"
#     f"{settings.rabbitmq.password}@{settings.rabbitmq.host}:"
#     f"{settings.rabbitmq.port}/{settings.rabbitmq.vhost}"
# )

# rabbit_args = (rabbitmq_url, settings.rabbitmq.exchange)