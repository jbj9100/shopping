import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal
from models.user import User, UserSession
from db.redis_conn import redis_pool
import redis.asyncio as redis
from db.db_conn import AsyncSessionLocal
from repositories import rep_usersession_id_check

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class SessionContext:
    session_id: str
    user_id: int
    user: Optional[User] = None
    expires_at: Optional[datetime] = None
    source: Literal["redis", "db"] = "redis"

async def resolve_session(sid: str) -> Optional[SessionContext]:
    """
    세션 ID를 받아 Redis -> DB 순으로 조회하여 유효한 세션 컨텍스트를 반환.
    없거나 만료되었으면 None 반환.
    """
    if not sid:
        return None

    # 1. Redis Check
    redis_client = redis.Redis(connection_pool=redis_pool)
    user_id_str = None
    try:
        user_id_str = await redis_client.get(f"sess:{sid}")
    except Exception as e:
        logger.warning(f"Redis get error: {e}")
    finally:
        await redis_client.close()

    if user_id_str:
        # Redis Hit
        async with AsyncSessionLocal() as db:
            user = await db.get(User, int(user_id_str))
            if user:
                return SessionContext(
                    session_id=sid,
                    user_id=user.id,
                    user=user,
                    source="redis"
                )
            # 유저가 DB에 없으면(삭제됨) 무효

    # 2. Redis Miss -> DB Fallback ( & Warming)
    async with AsyncSessionLocal() as db:
        sess = await rep_usersession_id_check.DB_get_by_session_id(db, sid, load_user=True)
        if sess and rep_usersession_id_check.session_is_valid(sess):
            # Warming
            redis_c = redis.Redis(connection_pool=redis_pool)
            try:
                # TTL 7일 (하드코딩된 부분은 필요시 상수로 관리)
                await redis_c.setex(f"sess:{sid}", 60 * 60 * 24 * 7, str(sess.user_id))
            except Exception as e:
                logger.warning(f"Redis warming error: {e}")
            finally:
                await redis_c.close()
            
            return SessionContext(
                session_id=sid,
                user_id=sess.user_id,
                user=sess.user,
                expires_at=sess.expires_at,
                source="db"
            )

    return None
