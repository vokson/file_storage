import logging
from uuid import uuid4
from collections import OrderedDict

import pytest
import pytest_asyncio

from backend.core import exceptions
from backend.core.config import settings, tz_now
from backend.tests.src.repository import mixins

logger = logging.getLogger()


class TestBrokerMessageRepository(
    mixins.CommonMixin, mixins.AccountMixin, mixins.BrokerMessageMixin
):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, rollback_pg):
        self._conn = rollback_pg
        self._account_id, _ = await self._create_default_account(rollback_pg)

    @pytest.mark.asyncio
    async def test_get_by_id(self, rollback_broker_message_repository):
        id = await self._create_default_in_broker_message(self._conn)
        model = await rollback_broker_message_repository.get_by_id(id)
        self._cmp(self.DEFAULT_IN_BROKER_MESSAGE_PARAMETERS, model)

        id = await self._create_default_out_broker_message(self._conn)
        model = await rollback_broker_message_repository.get_by_id(id)
        self._cmp(self.DEFAULT_OUT_BROKER_MESSAGE_PARAMETERS, model)

    @pytest.mark.asyncio
    async def test_get_by_id_if_not_exist(
        self, rollback_broker_message_repository
    ):
        with pytest.raises(exceptions.FileNotFound):
            await rollback_broker_message_repository.get_by_id(uuid4())

    @pytest.mark.asyncio
    async def test_get_not_executed_out(
        self, rollback_broker_message_repository
    ):
        chunk_size = 10
        args = OrderedDict(
            [
                ("id", uuid4()),
                ("direction", "O"),
                ("app", "APP"),
                ("key", "KEY"),
                ("body", {"key": "value"}),
                ("has_executed", True),
                ("created", tz_now()),
                ("updated", tz_now()),
                ("has_execution_stopped", False),
                ("count_of_retries", 0),
                ("next_retry_at", tz_now()),
                ("seconds_to_next_retry", 1),
            ]
        )
        await self._create_broker_message(self._conn, *args.values())

        args = OrderedDict(
            [
                ("id", uuid4()),
                ("direction", "O"),
                ("app", "APP"),
                ("key", "KEY"),
                ("body", {"key": "value"}),
                ("has_executed", False),
                ("created", tz_now()),
                ("updated", tz_now()),
                ("has_execution_stopped", True),
                ("count_of_retries", 0),
                ("next_retry_at", tz_now()),
                ("seconds_to_next_retry", 1),
            ]
        )
        await self._create_broker_message(self._conn, *args.values())

        id = await self._create_default_out_broker_message(self._conn)

        models = (
            await rollback_broker_message_repository.get_not_executed_outgoing(
                chunk_size
            )
        )
        assert len(models) == 1
        assert models[0].id == id

    @pytest.mark.asyncio
    async def test_get_not_executed_in(
        self, rollback_broker_message_repository
    ):
        chunk_size = 10
        args = OrderedDict(
            [
                ("id", uuid4()),
                ("direction", "I"),
                ("app", "APP"),
                ("key", "KEY"),
                ("body", {"key": "value"}),
                ("has_executed", True),
                ("created", tz_now()),
                ("updated", tz_now()),
                ("has_execution_stopped", False),
                ("count_of_retries", 0),
                ("next_retry_at", tz_now()),
                ("seconds_to_next_retry", 1),
            ]
        )
        await self._create_broker_message(self._conn, *args.values())

        args = OrderedDict(
            [
                ("id", uuid4()),
                ("direction", "I"),
                ("app", "APP"),
                ("key", "KEY"),
                ("body", {"key": "value"}),
                ("has_executed", False),
                ("created", tz_now()),
                ("updated", tz_now()),
                ("has_execution_stopped", True),
                ("count_of_retries", 0),
                ("next_retry_at", tz_now()),
                ("seconds_to_next_retry", 1),
            ]
        )
        await self._create_broker_message(self._conn, *args.values())

        id = await self._create_default_in_broker_message(self._conn)

        models = (
            await rollback_broker_message_repository.get_not_executed_incoming(
                chunk_size
            )
        )
        assert len(models) == 1
        assert models[0].id == id

    @pytest.mark.asyncio
    async def test_add_outgoing(self, rollback_broker_message_repository):
        key = "KEY"
        body = {"key": "value"}
        delay_in_seconds = 100

        model = await rollback_broker_message_repository.add_outgoing(
            key, body, delay_in_seconds
        )

        query = f"""
                SELECT * FROM {settings.broker_messages_table}
                WHERE
                    id = $1 AND
                    app = $2 AND
                    key = $3 AND
                    body = $4::jsonb AND
                    direction = 'O';
                """
        row = await self._conn.fetchrow(
            query,
            model.id,
            settings.app_name,
            key,
            body,
        )

        assert row is not None
        assert row["app"] == settings.app_name
        assert row["key"] == key
        assert row["body"] == body
        assert row["has_executed"] == False
        assert row["has_execution_stopped"] == False
        assert row["count_of_retries"] == 0
        assert row["seconds_to_next_retry"] == 1
        assert (
            int((row["next_retry_at"] - row["created"]).total_seconds())
            == delay_in_seconds
        )

    @pytest.mark.asyncio
    async def test_add_incoming(self, rollback_broker_message_repository):
        id = uuid4()
        app = "APP"
        key = "KEY"
        body = {"key": "value"}

        model = await rollback_broker_message_repository.add_incoming(
            id, app, key, body
        )

        query = f"""
                SELECT * FROM {settings.broker_messages_table}
                WHERE
                    id = $1 AND
                    app = $2 AND
                    key = $3 AND
                    body = $4::jsonb AND
                    direction = 'I';
                """
        row = await self._conn.fetchrow(
            query,
            model.id,
            app,
            key,
            body,
        )

        assert row is not None
        assert row["app"] == app
        assert row["key"] == key
        assert row["body"] == body
        assert row["has_executed"] == False
        assert row["has_execution_stopped"] == False
        assert row["count_of_retries"] == 0
        assert row["seconds_to_next_retry"] == 1
        assert (
            int((row["next_retry_at"] - row["created"]).total_seconds()) == 0
        )

    @pytest.mark.asyncio
    async def test_mark_as_executed(self, rollback_broker_message_repository):
        id = await self._create_default_out_broker_message(self._conn)
        await rollback_broker_message_repository.mark_as_executed([id])
        query = f"""
                SELECT * FROM {settings.broker_messages_table}
                WHERE
                    id = $1 AND
                    has_executed = TRUE;
                """
        row = await self._conn.fetchrow(
            query,
            id,
        )

        assert row is not None

    @pytest.mark.asyncio
    async def test_schedule_next_retry(
        self, rollback_broker_message_repository
    ):
        id = await self._create_default_out_broker_message(self._conn)
        count_of_retries = 0
        seconds_to_next_retry = 1

        async def schedule_next():
            await rollback_broker_message_repository.schedule_next_retry([id])

            nonlocal count_of_retries
            count_of_retries += 1

            nonlocal seconds_to_next_retry
            seconds_to_next_retry *= 2

        await schedule_next()

        query = f"""
                SELECT * FROM {settings.broker_messages_table}
                WHERE
                    id = $1 AND
                    has_executed = FALSE AND
                    count_of_retries = $2 AND
                    seconds_to_next_retry = $3;
                """

        row = await self._conn.fetchrow(
            query, id, count_of_retries, seconds_to_next_retry
        )

        assert row is not None

        query = f"""
                SELECT * FROM {settings.broker_messages_table}
                WHERE id = $1;
                """

        for _ in range(settings.broker.publish_retry_count-1):
            await schedule_next()
            row = await self._conn.fetchrow(
                query, id
            )
            print(row)

        assert row is not None
        assert row['has_executed'] is False
        assert row['has_execution_stopped'] is True
        
