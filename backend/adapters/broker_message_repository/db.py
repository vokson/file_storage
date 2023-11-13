import logging
from uuid import UUID, uuid4

from backend.core import exceptions
from backend.core.config import settings, tz_now
from backend.domain.models import BrokerMessage

from .abstract import AbstractBrokerMessageRepository

logger = logging.getLogger(__name__)


class DatabaseBrokerMessageRepository(AbstractBrokerMessageRepository):
    GET_BY_ID_QUERY = (
        f"SELECT * FROM {settings.broker_messages_table} WHERE id = $1;"
    )

    GET_NOT_EXECUTED_MESSAGES_QUERY = f"""
                        SELECT * FROM {settings.broker_messages_table}
                        WHERE
                            direction = $1 AND
                            has_executed = FALSE AND
                            has_execution_stopped = FALSE AND
                            next_retry_at < $2
                        LIMIT $3;
                        """

    ADD_QUERY = f"""
                    INSERT INTO {settings.broker_messages_table}
                        (
                            id,
                            direction,
                            app,
                            "key",
                            body,
                            has_executed,
                            created,
                            updated,
                            has_execution_stopped,
                            count_of_retries,
                            next_retry_at,
                            seconds_to_next_retry
                        )
                    VALUES
                        ($1, $2, $3, $4, $5::jsonb, $6, $7, $8, $9, $10, $11, $12);
                    """

    MARK_AS_EXECUTED_QUERY = f"""
                            UPDATE {settings.broker_messages_table}
                            SET updated = $2, has_executed = TRUE
                            WHERE id = ANY($1::uuid[]);
                        """

# TODO Сложение int и timestamp
    SCHEDULE_NEXT_RETRY_QUERY = f"""
                            UPDATE {settings.broker_messages_table}
                            SET
                                updated = $2,
                                count_of_retries = count_of_retries + 1,
                                next_retry_at = $2 + seconds_to_next_retry,
                                seconds_to_next_retry = seconds_to_next_retry * 2
                            WHERE id = ANY($1::uuid[]);
                        """

    MARK_AS_FAILED_QUERY = f"""
                            UPDATE {settings.broker_messages_table}
                            SET has_execution_stopped = TRUE
                            WHERE id = ANY($1::uuid[]) AND count_of_retries >= $2;
                        """

    async def get_by_id(self, id: UUID) -> BrokerMessage:
        logger.debug(f"Get broker message with id {id}.")
        row = await self._conn.fetchrow(self.GET_BY_ID_QUERY, id)
        if not row:
            raise exceptions.FileNotFound

        return self._convert_row_to_obj(row)

    async def _get_not_executed(
        self, direction: str, chunk_size: int
    ) -> list[BrokerMessage]:
        logger.debug(f"Get not executed {direction} broker messages.")
        rows = await self._conn.fetch(
            self.GET_NOT_EXECUTED_MESSAGES_QUERY,
            direction,
            tz_now(),
            chunk_size,
        )
        return [self._convert_row_to_obj(x) for x in rows]

    async def get_not_executed_outgoing(
        self, chunk_size: int
    ) -> list[BrokerMessage]:
        return await self._get_not_executed(self.OUT_DIRECTION, chunk_size)

    async def _add(
        self,
        direction: str,
        app: str,
        key: str,
        body: dict,
        delay_in_seconds: int,
    ):
        id = uuid4()
        logger.debug(
            f"""
            Add broker message with id {id}, direction {direction},
            app {app}, key {key}, body {body}, delay in seconds {delay_in_seconds}
            """
        )

        await self._conn.execute(
            self.ADD_QUERY,
            id,
            direction,
            app,
            key,
            body,
            False,
            tz_now(),
            tz_now(),
            False,
            settings.broker.publish_retry_count,
            tz_now(delay_in_seconds),
            1,
        )

        await self.get_by_id(id)

    async def add_outgoing(self, key: str, body: dict, delay_in_seconds: int):
        await self._add(
            self.OUT_DIRECTION, settings.app_name, key, body, delay_in_seconds
        )

    async def add_incoming(self, id: UUID, app: str, key: str, body: dict):
        if self.get_by_id(id):
            return

        await self._add(self.IN_DIRECTION, app, key, body, 0)

    async def mark_as_executed(self, ids: list[UUID]):
        logger.debug(f"Mark broker messages as executed. IDs: {ids}")
        await self._conn.execute(self.MARK_AS_EXECUTED_QUERY, ids, tz_now())

    async def schedule_next_retry(self, ids: list[UUID]):
        logger.debug(f"Schedule next retry for broker messages. IDs: {ids} ")
        await self._conn.execute(
            self.SCHEDULE_NEXT_RETRY_QUERY,
            ids,
            tz_now(),
        )
        # await self._conn.execute(
        #     self.MARK_AS_FAILED_QUERY,
        #     ids,
        #     settings.broker.publish_retry_count,
        # )


async def get_db_broker_message_repository(
    conn,
) -> AbstractBrokerMessageRepository:
    return DatabaseBrokerMessageRepository(conn)
