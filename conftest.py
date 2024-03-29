" Настройки для локального тестирования"

import asyncio

import pytest

pytest_plugins = (
    "backend.tests.utils.fixtures.storage",
    "backend.tests.utils.fixtures.pg",
    "backend.tests.utils.fixtures.bus",
)


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
