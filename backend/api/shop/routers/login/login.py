from fastapi import APIRouter, Request, Depends, Response
from schemas.sc_user import LoginIn, UserUpdateIn
from sqlalchemy.ext.asyncio import AsyncSession
from db.conn_db import get_session
from db.conn_redis import get_redis
from core.auth import auth_login
from services.cookie.svc_session import rotate_session
from services.cookie.svc_cookie_setting import cookie_settings
from services.redis.redis_session_context import resolve_session

router = APIRouter(prefix="/api/shop/login", tags=["login"])

@router.get("/")
def login_get():
    return {"message": "login page"}

@router.post("/")
async def login(login_in: LoginIn, request: Request, response: Response,
                db: AsyncSession = Depends(get_session),
                redis_client = Depends(get_redis)) -> dict:
    print("성공1")
    user = await auth_login.auth_verify(db, login_in.email, login_in.password)
    print("성공2")
    old_sid = request.cookies.get(cookie_settings.COOKIE_NAME)
    print("성공3")
    sess_id = await rotate_session(db, user_id=user.id, old_sid=old_sid, redis_client=redis_client)
    print("성공4")

    response.set_cookie(
        key=cookie_settings.COOKIE_NAME,
        value=sess_id,
        max_age=cookie_settings.COOKIE_TTL_SECONDS,
        secure=cookie_settings.COOKIE_SECURE,
        httponly=cookie_settings.COOKIE_HTTPONLY,
        samesite=cookie_settings.COOKIE_SAMESITE,
        path=cookie_settings.COOKIE_PATH,
        domain=None,  # ← localhost에서 작동하도록
    )

    print(f"로그인 성공: {user.username}, 세션 ID: {sess_id}")
    return { "ok": True }
