import pytest
import asyncio

import pathlib

from config import Settings


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def root_dir():
    return pathlib.Path(__file__).parent.parent.parent


@pytest.fixture(scope='session')
def settings(root_dir):
    return Settings()
