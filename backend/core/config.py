# import os
# from datetime import datetime, timedelta
from logging import config as logging_config

from backend.core.logger import LOGGING

# from pydantic import BaseModel, BaseSettings, Field


logging_config.dictConfig(LOGGING)


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ENV_DIR = os.path.join(BASE_DIR, "..", "..")


# class DatabaseSettings(BaseModel):
#     host: str
#     port: int
#     user: str
#     password: str
#     dbname: str


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


# class Settings(BaseSettings):
#     debug: bool
#     app_name: str
#     auth: AuthServiceSettings
#     storage_db: DatabaseSettings
#     cache: CacheSettings
#     s3: S3Settings
#     geo: GeoSettings
#     rabbitmq: RabbitSettings
#     storage_path: str = Field("/temp_storage")

#     class Config:
#         #  Для локальной разработки вне docker
#         env_file = (
#             os.path.join(ENV_DIR, ".env"),
#             os.path.join(ENV_DIR, ".env.dev"),
#         )
#         env_nested_delimiter = "__"


# settings = Settings()


# def tz_now():
#     return datetime.now() + timedelta(hours=3)  # Moscow Time


# db_dsl = {
#     "host": settings.storage_db.host,
#     "port": settings.storage_db.port,
#     "user": settings.storage_db.user,
#     "database": settings.storage_db.dbname,
#     "password": settings.storage_db.password,
# }

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