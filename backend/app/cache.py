"""
Redis client management.
Returns None if redis_url is not configured (optional dependency).
"""
import redis.asyncio as aioredis

from app.config import get_settings

_redis_client: aioredis.Redis | None = None


async def get_redis_client() -> aioredis.Redis | None:
    """
    Returns a connected async Redis client, or None if redis_url is not set.
    Reuses a module-level singleton to avoid reconnecting on every request.
    """
    global _redis_client
    settings = get_settings()

    if settings.redis_url is None:
        return None

    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    return _redis_client
