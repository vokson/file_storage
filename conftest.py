" Настройки для локального тестирования"

import asyncio
import os
import sys

import pytest

pytest_plugins = "backend.tests.utils.fixtures.storage", "backend.tests.utils.fixtures.pg",


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
