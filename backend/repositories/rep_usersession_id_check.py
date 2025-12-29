from datetime import datetime
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from models.user import UserSession
from fastapi import HTTPException, Request


def _now() -> datetime:
    return datetime.now()

####미들웨어가 쿠키 sid를 검증할 때####
# 세션이 살아있는지 판정(만료/폐기 확인)하는 함수로 revoked_at와 expires_at이 없으면 True로 유효한 세션
def session_is_valid(sess: UserSession) -> bool:
    if sess.revoked_at is not None: # revoked_at이 있으면 로그아웃/강제폐기된 세션 
        return False
    if sess.expires_at <= _now():
        return False
    return True

####미들웨어가 쿠키 sid를 검증할 때####
# 쿠키에 들어있는 sid(=세션 id)를 가지고, DB에서 user_sessions 테이블의 “그 세션 row”를 찾아오는 함수
async def DB_get_by_session_id(db: AsyncSession, session_id: str,*, load_user: bool = True) -> Optional[UserSession]:
    stmt = select(UserSession).where(UserSession.id == session_id)
    if load_user:
        stmt = stmt.options(joinedload(UserSession.user))  # Detached 방지(권한 체크용)
    return await db.scalar(stmt)


async def DB_get_by_user(db: AsyncSession, request: Request) -> str:
    sid = request.cookies.get("sid")  # standard cookie name in this project
    sess = await DB_get_by_session_id(db, sid, load_user=True)

    if not sess or not session_is_valid(sess):
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return sess.user.username