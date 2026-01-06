from sqlalchemy.ext.asyncio import AsyncSession
from repositories.usersession.rep_get_del import DB_create_session_id, DB_revoke_session_id
from services.cookie.svc_cookie_setting import cookie_settings


# 로그인/로그아웃 같은 “행동(비즈니스 이벤트)”이 발생했을 때 DB 작업 + 쿠키 반영까지 한 번에 끝내는 곳


# 로그인 성공했을 때 세션 발급
async def issue_session(db: AsyncSession, user_id: int, redis_client=None) -> str:
    sess = await DB_create_session_id(db, user_id=user_id )
    await db.commit()
    # Redis Caching
    if redis_client:
            await redis_client.setex(
            f"sess:{sess.id}",  
            cookie_settings.COOKIE_TTL_SECONDS,
            str(user_id)
        )

    return sess.id

# 기존 sid가 있으면 폐기(revoke) + 새 세션 발급 + 새 쿠키 세팅
async def rotate_session(db: AsyncSession, user_id: int, old_sid: str, redis_client=None) -> str:
    if old_sid:
        await DB_revoke_session_id(db, session_id=old_sid)
        # Redis Del
        if redis_client:
            await redis_client.delete(f"sess:{old_sid}")
    
    new_sess = await DB_create_session_id(db, user_id=user_id)
    await db.commit()
    # Redis Set
    if redis_client:
        await redis_client.setex(
            f"sess:{new_sess.id}",
            cookie_settings.COOKIE_TTL_SECONDS,
            str(user_id)
        )

    return new_sess.id

# 현재 sid 폐기 + 쿠키 삭제
async def delete_session(db: AsyncSession, old_sid: str, redis_client=None) -> None:
    if old_sid:
        await DB_revoke_session_id(db, session_id=old_sid)
        await db.commit()
        if redis_client:
            await redis_client.delete(f"sess:{old_sid}")

    return old_sid

