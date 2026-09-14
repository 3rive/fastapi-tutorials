import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.infrastructure.persistence.mongodb.database import (
    close_mongo_connection,
    init_database,
)
from app.main import create_app


@pytest.fixture(scope="session")
def mongodb_uri() -> str:
    return os.environ.get("MONGODB_URI", "mongodb://localhost:27017")


@pytest.fixture(scope="session")
def mongodb_database() -> str:
    return os.environ.get("MONGODB_TEST_DATABASE", "fastapi_tutorials_test")


@pytest.fixture
async def app(mongodb_uri: str, mongodb_database: str) -> AsyncIterator:
    os.environ["MONGODB_URI"] = mongodb_uri
    os.environ["MONGODB_DATABASE"] = mongodb_database
    get_settings.cache_clear()
    application = create_app()
    await init_database()
    yield application
    await close_mongo_connection()
    get_settings.cache_clear()


@pytest.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def clean_users_collection(app) -> AsyncIterator[None]:
    from app.infrastructure.persistence.mongodb.database import get_database

    await get_database().users.delete_many({})
    yield
