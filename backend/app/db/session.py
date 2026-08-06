from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

connect_args = {}
if "postgresql" in settings.DATABASE_URL and "localhost" not in settings.DATABASE_URL and "127.0.0.1" not in settings.DATABASE_URL:
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ctx

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True, connect_args=connect_args)
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
