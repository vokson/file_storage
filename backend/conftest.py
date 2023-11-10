" Настройки для тестирования внутри Docker"

import asyncio
import os
import sys

import pytest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, ROOT_DIR)


pytest_plugins = (
    "tests.utils.fixtures.storage",
    "tests.utils.fixtures.pg",
    "tests.utils.fixtures.bus",
)


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
