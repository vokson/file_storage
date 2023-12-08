import asyncio
import logging
from abc import ABC, abstractmethod

from backend.service_layer.message_bus import MessageBus
from backend.tools.delay import DelayCalculator

logger = logging.getLogger()


class AbstractWorker(ABC):
    def __init__(
        self,
        bus: MessageBus,
        delay_calculator=DelayCalculator(limit=1),
        chunk_size: int = 1000,
    ):
        self._bus = bus
        self._delay_calculator = delay_calculator
        self._chunk_size = chunk_size

    async def run(self, name: str):
        while True:
            try:
                await self._do()
            except Exception as e:
                logger.error(f"Error in {name} during running")
                logger.info(e)

            sleep_time = self._delay_calculator.get()
            logger.info(f"{name} sleeping {sleep_time} seconds.")
            await asyncio.sleep(sleep_time)

    @abstractmethod
    async def _do(self):
        pass
