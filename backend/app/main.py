from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import init_db


def _rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please slow down and retry."},
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Create missing tables and seed data if empty
    await init_db()
    try:
        from app.db.session import AsyncSessionLocal
        from sqlalchemy import select
        from app.models.entities import WalletReputation
        from scripts.seed import seed_all
        async with AsyncSessionLocal() as db:
            count = (await db.execute(select(WalletReputation).limit(1))).scalar_one_or_none()
            if count is None:
                print("Seeding database automatically on startup...")
                await seed_all(db)
    except Exception as e:
        print(f"Startup seeding notice: {e}")

    # Launch the live Horizon ingestor (opt-in via INGESTOR_ENABLED).
    if settings.INGESTOR_ENABLED:
        try:
            from app.services.ingestor import start_ingestor
            await start_ingestor()
        except Exception as e:
            print(f"Ingestor startup notice: {e}")

    yield

    if settings.INGESTOR_ENABLED:
        try:
            from app.services.ingestor import stop_ingestor
            await stop_ingestor()
        except Exception as e:
            print(f"Ingestor shutdown notice: {e}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.state.limiter = limiter
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health():
    """Liveness probe for orchestrators and load balancers."""
    return {"status": "ok", "service": settings.PROJECT_NAME, "version": settings.VERSION}
