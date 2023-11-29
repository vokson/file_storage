import asyncio
import hashlib
import json
import logging
from abc import ABC, abstractmethod
from typing import Awaitable, Callable
from uuid import UUID

import aioamqp
from aioamqp.protocol import CONNECTING, OPEN

from backend.tools.delay import DelayCalculator

logger = logging.getLogger(__name__)


class AbstractRabbitExchangeConnector(ABC):
    def __init__(
        self,
        ampq_url,
        exchange,
        exchange_type="topic",
        exchange_durability=True,
        delay_calculator=DelayCalculator(limit=30),
    ):
        self._url = ampq_url
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._exchange_durability = exchange_durability
        self._delay_calculator = delay_calculator

        self._connection = None
        self._closing = False
        self._interval_in_sec = 0

    async def run(self):
        self._should_reconnect = True
        while True:
            await self._maybe_reconnect()

    def set_interval(self, value: int):
        logger.info(f"Set interval {value} seconds")
        self._interval_in_sec = 0 if value < 0 else value

    async def _run(self):
        try:
            self._should_reconnect = False
            await self._connect()
            await self._open_channel()
            await self._actions()
        except aioamqp.AmqpClosedConnection as e:
            logger.warning("Connection closed")
            logger.info(e)

        except (aioamqp.AioamqpException, ConnectionRefusedError) as e:
            await self._on_connection_error(e)

    @abstractmethod
    async def _actions(self):
        pass

    async def _connect(self):
        if self._connection and self._connection.state in [OPEN, CONNECTING]:
            logger.info("Connection is connecting or already opened")
            return

        logger.info("Connecting..")

        transport, protocol = await aioamqp.from_url(
            self._url,
            on_error=self._on_connection_error,
        )

        self._connection = protocol
        logger.warning("Connection opened")

    async def _open_channel(self):
        logger.warning("Creating a new channel")
        self._channel = await self._connection.channel()
        logger.warning("Channel opened")

    async def _setup_exchange(self, exchange_name, exchange_type):
        logger.warning("Declaring exchange %s", exchange_name)
        await self._channel.exchange_declare(
            exchange_name,
            exchange_type,
            durable=self._exchange_durability,
        )
        logger.warning("Exchange declared: %s", exchange_name)

    async def _on_connection_error(self, err):
        self._channel = None

        if not self._closing:
            self._should_reconnect = True
            await self._stop_and_close()
            logger.warning("Connection closed, reconnect necessary: %s", err)

    async def _reconnect(self):
        self._should_reconnect = True
        await self._maybe_reconnect()

    async def _stop_and_close(self):
        await self._stop()

        if self._channel:
            await self._channel.close()

    @abstractmethod
    async def _stop(self):
        pass

    async def _maybe_reconnect(self):
        await asyncio.sleep(1)
        if not self._should_reconnect:
            return

        reconnect_delay = self._delay_calculator.get()
        logger.warning("Reconnecting after %d seconds", reconnect_delay)
        await asyncio.sleep(reconnect_delay)

        await self._run()

    def _reset_delay(self):
        self._delay_calculator.done()


class RabbitPublisher(AbstractRabbitExchangeConnector):
    def __init__(
        self,
        ampq_url,
        exchange,
        exchange_type="topic",
        exchange_durability=True,
        delay_calculator=DelayCalculator(limit=30),
    ):
        super().__init__(
            ampq_url,
            exchange,
            exchange_type=exchange_type,
            exchange_durability=exchange_durability,
            delay_calculator=delay_calculator,
        )
        self._content_type = "application/json"

    async def _actions(self):
        await self._setup_exchange(self._exchange, self._exchange_type)
        await self._start_publishing()

    async def _start_publishing(self):
        logger.info("Issuing consumer related RPC commands")
        await self._channel.confirm_select()

    async def push_message(self, app, key, body, id: UUID | None = None):
        logger.info("Push new message")

        if self._channel is None or not self._channel.is_open:
            self._should_reconnect = True
            return False

        logger.info(f"Sleep {self._interval_in_sec} before push message")
        await asyncio.sleep(self._interval_in_sec)

        json_body = json.dumps(body, default=str).encode()

        uid = (
            str(id)
            if id
            else self._make_hash(app.encode(), key.encode(), json_body)
        )

        properties = {
            "message_id": uid,
            "app_id": app,
            "content_type": self._content_type,
        }

        try:
            await self._channel.publish(
                json_body,
                self._exchange,
                routing_key=key,
                properties=properties,
            )
            logger.info(f"Published message uid: {uid}")
            self._reset_delay()
            return True

        except Exception as e:
            logger.error(f"Not published: {uid}")
            logger.info(e)
            return False

    def _make_hash(self, app, key, content):
        h = hashlib.md5()  # noqa: S324

        h.update(app)
        h.update(key)
        h.update(content)

        return h.hexdigest()

    async def _stop(self):
        await super()._stop()


class RabbitConsumer(AbstractRabbitExchangeConnector):
    def __init__(
        self,
        ampq_url,
        exchange,
        queue,
        on_consume_message_callback: Callable[
            [str, str, str, dict], Awaitable[bool]
        ],
        routing_key="#",
        exchange_type="topic",
        exchange_durability=True,
        queue_durability=True,
        delay_calculator=DelayCalculator(limit=30),
        cache=None,
    ):
        super().__init__(
            ampq_url,
            exchange,
            exchange_type=exchange_type,
            exchange_durability=exchange_durability,
            delay_calculator=delay_calculator,
        )

        self._dead_letter_exchange = f"{exchange}-dead-letter"
        self._queue_durability = queue_durability
        self._queue = queue
        self._callback = on_consume_message_callback
        self._routing_key = routing_key

        self._cache = cache
        self._consumer_tag = None
        self._prefetch_count = 1

    async def _actions(self):
        await self._setup_exchange(self._exchange, self._exchange_type)
        await self._setup_exchange(
            self._dead_letter_exchange,
            self._exchange_type,
        )
        await self._setup_queue(
            self._queue,
            self._queue_durability,
            self._dead_letter_exchange,
        )
        await self._start_consuming()

    async def _setup_queue(
        self,
        queue_name,
        queue_durability,
        dead_letter_exchange,
    ):
        logger.info("Declaring queue %s", queue_name)

        args = {"x-dead-letter-exchange": dead_letter_exchange}
        await self._channel.queue_declare(
            queue_name=queue_name,
            durable=queue_durability,
            arguments=args,
        )
        logger.info(
            "Binding %s to %s with %s",
            self._exchange,
            queue_name,
            self._routing_key,
        )

        await self._channel.queue_bind(
            queue_name,
            self._exchange,
            self._routing_key,
        )
        logger.info("Queue bound: %s", queue_name)

        await self._channel.basic_qos(prefetch_count=self._prefetch_count)
        logger.info("QOS set to: %d", self._prefetch_count)

    async def _start_consuming(self):
        logger.info("Issuing consumer related RPC commands")

        logger.warning("Adding consumer cancellation callback")
        self._channel.add_cancellation_callback(self._on_consumer_cancelled)

        response = await self._channel.basic_consume(
            self._on_message,
            self._queue,
        )

        self._consumer_tag = response["consumer_tag"]
        self._delay_calculator.done()

    async def _on_consumer_cancelled(self, _unused_channel, consumer_tag):
        logger.info(
            "Consumer was cancelled remotely, shutting down: %r",
            consumer_tag,
        )
        if self._channel:
            await self._channel.close()

    async def _on_message(self, _unused_channel, body, envelope, properties):
        logger.info(
            "Received message # %s from %s: %s-%s",
            envelope.delivery_tag,
            properties.app_id,
            properties.message_id,
            envelope.routing_key,
        )

        logger.info(f"Sleep {self._interval_in_sec} before consume message")
        await asyncio.sleep(self._interval_in_sec)

        is_new_message = True
        if self._cache and properties.message_id:
            # Проверяем установлен message_id в кэше,
            # чтобы исключить повторную обработку сообщения
            is_new_message = (
                not await self._cache.get(properties.message_id) == 1
            )

        if not is_new_message:
            logger.warning(
                f"Message with {properties.message_id}"
                f" has been already processed.",
            )
            await self._channel.basic_client_ack(envelope.delivery_tag)
            return

        try:
            # Обрабатываем полученное сообщение
            data = (
                properties.message_id,
                properties.app_id,
                envelope.routing_key,
                json.loads(body),
            )
        except json.decoder.JSONDecodeError:
            logger.info(
                f"JSONDecodeError during parsing of body"
                f" of RabbitMQ message {properties.message_id}",
            )
            return
        except Exception as e:
            logger.info(
                f"Unknown exception {e} during parsing of body"
                f" of RabbitMQ message {properties.message_id}",
            )
            return

        is_executed_successfully = await self._callback(*data)

        if is_executed_successfully:
            logger.info("Acknowledging message %s", envelope.delivery_tag)
            await self._channel.basic_client_ack(envelope.delivery_tag)

            if self._cache and properties.message_id:
                # Устанавливаем message_id в кэш,
                # чтобы исключить повторную обработку сообщения
                await self._cache.set(properties.message_id, 1)
        else:
            logger.info(
                "Send message %s to Dead Letter Exchange",
                envelope.delivery_tag,
            )
            await self._channel.basic_client_nack(
                envelope.delivery_tag,
                requeue=False,
            )

    async def _stop(self):
        if self._channel:
            logger.info("Sending a Basic.Cancel RPC command to RabbitMQ")
            await self._channel.basic_cancel(self._consumer_tag)

        await super()._stop()


publisher: RabbitPublisher | None = None
consumer: RabbitConsumer | None = None


async def init_publisher(*args, **kwargs):
    global publisher

    if not publisher:
        logger.info("Initialization of publisher ..")
        publisher = RabbitPublisher(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.create_task(publisher.run())
        logger.info("Publisher has been initialized.")

    return publisher


async def init_consumer(*args, **kwargs):
    global consumer

    if not consumer:
        logger.info("Initialization of consumer ..")
        consumer = RabbitConsumer(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.create_task(consumer.run())
        logger.info("Consumer has been initialized.")

    return consumer
