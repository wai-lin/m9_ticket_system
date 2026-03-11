"""Redis connection manager"""
import redis.asyncio as redis
from src.env import REDIS_URL


async def get_redis() -> redis.Redis:
    """Get a Redis connection"""
    return redis.from_url(REDIS_URL, decode_responses=False)
