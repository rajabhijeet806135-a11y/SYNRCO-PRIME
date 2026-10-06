import pytest
import pytest_asyncio
import asyncio
import os
import aiosqlite
from httpx import AsyncClient, ASGITransport
from app.config import settings
from app.core.database import db_ledger, SCHEMA_SQL
from app.core.redis_state import redis_client
from app.datasets.seed_data import seed_database
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    # Use test db file
    settings.DB_FILE = "./test_syncro_prime_ledger.sqlite"
    db_ledger.db_path = settings.DB_FILE

    async with aiosqlite.connect(settings.DB_FILE) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()

    redis_client.flushall()
    await seed_database()

    yield

    # Cleanup test db
    if os.path.exists(settings.DB_FILE):
        try:
            os.remove(settings.DB_FILE)
        except Exception:
            pass

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
