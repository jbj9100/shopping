
from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.rep_usersession_get_del import DB_create_session_id, DB_revoke_session_id


# 로그인/로그아웃 같은 “행동(비즈니스 이벤트)”이 발생했을 때 DB 작업 + 쿠키 반영까지 한 번에 끝내는 곳

class SessionService:
    def __init__(
        self,
        cookie_name: str = "sid",
        ttl_seconds: int = 60 * 60 * 24 * 7,
        secure: bool = False,
        httponly: bool = True,
        samesite: str = "lax",
        path: str = "/",
    ):
        self.cookie_name = cookie_name
        self.ttl_seconds = ttl_seconds
        self.secure = secure
        self.httponly = httponly
        self.samesite = samesite
        self.path = path

    def _set_cookie(self, response: Response, sid: str) -> None:
        response.set_cookie(
            key=self.cookie_name,
            value=sid,
            max_age=self.ttl_seconds,
            secure=self.secure,
            httponly=self.httponly,
            samesite=self.samesite,
            path=self.path,
        )
# 로그인 성공했을 때 세션 발급
    async def issue_session(self, db: AsyncSession, user_id: int, response: Response, redis_client=None) -> str:
        sess = await DB_create_session_id(db, user_id=user_id, ttl_seconds=self.ttl_seconds)
        await db.commit()
        
        # Redis Caching
        if redis_client:
             await redis_client.setex(
                f"sess:{sess.id}",
                self.ttl_seconds,
                str(user_id)
            )

        self._set_cookie(response, sess.id)
        return sess.id

# 기존 sid가 있으면 폐기(revoke) + 새 세션 발급 + 새 쿠키 세팅
    async def rotate_session(self, db: AsyncSession, request: Request, user_id: int, response: Response, redis_client=None) -> str:
        old_sid = request.cookies.get(self.cookie_name)
        if old_sid:
            await DB_revoke_session_id(db, session_id=old_sid)
            # Redis Del
            if redis_client:
                await redis_client.delete(f"sess:{old_sid}")
        
        new_sess = await DB_create_session_id(db, user_id=user_id, ttl_seconds=self.ttl_seconds)
        await db.commit()
        # Redis Set
        if redis_client:
            await redis_client.setex(
                f"sess:{new_sess.id}",
                self.ttl_seconds,
                str(user_id)
            )

        self._set_cookie(response, new_sess.id)
        return new_sess.id

# 현재 sid 폐기 + 쿠키 삭제
    async def delete_session(self, db: AsyncSession, request: Request, response: Response, redis_client=None) -> None:
        sid = request.cookies.get(self.cookie_name)
        if sid:
            await DB_revoke_session_id(db, session_id=sid)
            await db.commit()
            if redis_client:
                await redis_client.delete(f"sess:{sid}")

        response.delete_cookie(key=self.cookie_name, path=self.path)

