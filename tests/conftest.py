import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.core.database import dispose_engine, init_database
from app.main import create_app


@pytest.fixture
async def app(tmp_path: Path) -> AsyncIterator:
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tmp_path / 'test.db'}"
    get_settings.cache_clear()
    await dispose_engine()
    application = create_app()
    await init_database()
    yield application
    await dispose_engine()
    get_settings.cache_clear()


@pytest.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
