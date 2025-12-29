import uuid
from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload
from models.user import UserSession

#### ORM CURD만 


def _now() -> datetime:
    return datetime.now()

####서비스가 로그인 성공 시 세션 발급할 때####
# 로그인 성공했을 때 세션 row를 하나 만드는 함수
async def DB_create_session_id(db: Session, user_id: int, ttl_seconds: int = 60 * 60 * 24 * 7) -> UserSession:
    now = _now()
    sess = UserSession(
        id=str(uuid.uuid4()),
        user_id=user_id,                      
        created_at=now,
        expires_at=now + timedelta(seconds=ttl_seconds),
        revoked_at=None,
    )
    db.add(sess)
    await db.commit()
    await db.refresh(sess)
    return sess

#### 서비스가 로그아웃 성공 시 폐기할 때####
# 로그아웃/강제폐기했을 때 세션 row를 하나 만드는 함수
# 세션을 “폐기” 처리 (삭제가 아님)
# row를 지우지 않고 revoked_at=now()로 표시만 해둠
async def DB_revoke_session_id(db: Session, session_id: str) -> None:
    await db.execute(
        update(UserSession)
        .where(UserSession.id == session_id)
        .values(revoked_at=_now())
    )
    await db.commit()

