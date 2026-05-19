"""Pytest configuration and shared fixtures."""
import os

# Provide safe defaults for required settings BEFORE any `app.*` import,
# so module-level `get_settings()` calls (e.g. app.middleware.rate_limit)
# don't fail on missing SECRET_KEY / DATABASE_URL when tests run without a .env.
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-used-in-prod")
# Use a postgres-format URL so app.database can construct its module-level
# engine with pool_size/max_overflow (postgres-only kwargs). The engine is
# lazy — it never connects. Tests open their own in-memory SQLite engine
# in the db_session fixture below.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/test",
)

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.database import Base

# Use in-memory SQLite for unit tests (no Postgres needed)
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use default event loop policy for pytest-asyncio."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture
async def db_session():
    """Provide a test database session backed by in-memory SQLite."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
