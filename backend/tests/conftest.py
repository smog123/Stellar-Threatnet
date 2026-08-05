import os

# Test configuration — MUST be set before importing the app.
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
os.environ.setdefault("CACHE_ENABLED", "false")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from datetime import datetime

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.session import Base, get_db
from app.main import app
from app.models.entities import User, UserRole

API_PREFIX = "/api/v1"


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(db_engine):
    return async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def client(db_engine):
    TestSession = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with TestSession() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def register_user(client, email: str, password: str = "super-secret-pass", full_name: str | None = None):
    resp = await client.post(
        f"{API_PREFIX}/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def auth_headers(client, email: str = "reporter@example.com") -> dict[str, str]:
    data = await register_user(client, email)
    return {"Authorization": f"Bearer {data['access_token']}"}


async def promote_user(session_factory, email: str, role: UserRole) -> None:
    async with session_factory() as db:
        user = (await db.execute(select(User).where(User.email == email))).scalar_one()
        user.role = role
        user.is_active = True
        await db.commit()


@pytest_asyncio.fixture
async def reporter_headers(client) -> dict[str, str]:
    return await auth_headers(client, "reporter@example.com")


@pytest_asyncio.fixture
async def analyst_headers(client, session_factory) -> dict[str, str]:
    headers = await auth_headers(client, "analyst@example.com")
    await promote_user(session_factory, "analyst@example.com", UserRole.ANALYST)
    return headers


@pytest_asyncio.fixture
async def moderator_headers(client, session_factory) -> dict[str, str]:
    headers = await auth_headers(client, "moderator@example.com")
    await promote_user(session_factory, "moderator@example.com", UserRole.MODERATOR)
    return headers
