from collections.abc import AsyncGenerator
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.database import get_db_session
from app.main import app
from app.models.base import Base


@pytest_asyncio.fixture
async def test_session(
    tmp_path: Path,
) -> AsyncGenerator[AsyncSession, None]:
    database_path = tmp_path / "test.db"
    database_url = f"sqlite+aiosqlite:///{database_path}"

    test_engine = create_async_engine(database_url)

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    await test_engine.dispose()


@pytest_asyncio.fixture
async def client(
    test_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db_session() -> (
        AsyncGenerator[AsyncSession, None]
    ):
        yield test_session

    app.dependency_overrides[get_db_session] = (
        override_get_db_session
    )

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()