"""Redis-backed lookup cache with graceful degradation.

If Redis is unreachable the cache silently falls back to no-ops so the API
keeps serving from PostgreSQL. This keeps local development and the test
suite dependency-free while production benefits from sub-20ms lookups.
"""
from typing import Any, Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings

_redis: Optional[Redis] = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def cache_get(key: str) -> Optional[str]:
    """Return the cached value or None (including when Redis is down)."""
    if not settings.CACHE_ENABLED:
        return None
    try:
        return await get_redis().get(key)
    except RedisError:
        return None


async def cache_set(key: str, value: str, ttl: Optional[int] = None) -> None:
    if not settings.CACHE_ENABLED:
        return
    try:
        await get_redis().set(key, value, ex=ttl or settings.CACHE_TTL_SECONDS)
    except RedisError:
        pass


async def cache_delete_pattern(pattern: str) -> None:
    """Best-effort deletion of all keys matching a glob pattern."""
    if not settings.CACHE_ENABLED:
        return
    try:
        redis = get_redis()
        async for key in redis.scan_iter(match=pattern, count=100):
            await redis.delete(key)
    except RedisError:
        pass


def cache_key(entity_type: str, identifier: str) -> str:
    return f"threatnet:{entity_type}:{identifier}"
