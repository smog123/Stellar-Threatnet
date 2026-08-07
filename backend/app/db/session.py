from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings


def _normalize_async_url(url: str) -> str:
    """Force an async driver onto the DB URL.

    Managed Postgres providers (Render, Heroku, …) inject bare
    ``postgresql://`` / ``postgres://`` URLs, which SQLAlchemy routes to the
    sync psycopg2 driver we don't ship — causing ``ModuleNotFoundError: No
    module named 'psycopg2'`` at startup. Rewrite the scheme to asyncpg.
    """
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://"):]
    return url


DATABASE_URL = _normalize_async_url(settings.DATABASE_URL)

connect_args = {}
if "postgresql" in DATABASE_URL and "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ctx

engine = create_async_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    """FastAPI dependency yielding an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables that do not yet exist.

    Development convenience only — production deployments must use
    `alembic upgrade head` (see docs/DEPLOYMENT.md).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
