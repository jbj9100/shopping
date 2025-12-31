import os
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")


redis_pool = redis.ConnectionPool.from_url(
    REDIS_URL,
    decode_responses=True,
    encoding="utf-8"
)

async def get_redis() -> redis.Redis:
    """Redis 클라이언트 의존성 주입용"""
    if redis_pool is None:
        raise Exception("Redis connection pool not initialized")
    client = redis.Redis(connection_pool=redis_pool)

    try:
        yield client
    finally:
        await client.close()

async def ping_redis() -> bool:
    try:
        client = redis.Redis(connection_pool=redis_pool)
        return bool(await client.ping())
    except Exception as e:
        print("Redis ping error:", repr(e))
        return False

async def close_redis() -> None:
    try:
        client = redis.Redis(connection_pool=redis_pool)
        await client.close()          
    except Exception as e:
        print("Redis close error:", repr(e))
