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

async def ping_redis() -> tuple[bool, str | None]:
    """
    Redis 연결 테스트
    
    Returns:
        (성공 여부, 에러 메시지 또는 None)
    """
    try:
        client = redis.Redis(connection_pool=redis_pool)
        await client.ping()
        return True, None
    except Exception as e:
        return False, f"Redis connection error: {str(e)}"

async def close_redis() -> None:
    try:
        client = redis.Redis(connection_pool=redis_pool)
        await client.close()          
    except Exception as e:
        print("Redis close error:", repr(e))
