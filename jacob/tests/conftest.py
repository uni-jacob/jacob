import asyncio

import pytest

from jacob.database.utils.init import init_db_connection


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def connect_database():
    await init_db_connection()
