from fastapi import APIRouter, Request, Response, Depends
from schemas.sc_user import LoginIn, UserUpdateIn
from sqlalchemy.ext.asyncio import AsyncSession
from db.conn_db import get_session
from db.conn_redis import get_redis
from core.auth import auth_login
from services.cookie.svc_session import SessionService
from services.redis.redis_session_context import resolve_session

router = APIRouter(prefix="/api/shop/login", tags=["login"])

@router.get("/")
def login_get():
    return {"message": "login page"}

@router.post("/")
async def login(login_in: LoginIn, request: Request, response: Response,
                db: AsyncSession = Depends(get_session),
                redis_client = Depends(get_redis)) -> dict:
    user = await auth_login.auth_verify(db, login_in.email, login_in.password)
    svc_session = SessionService()
    await svc_session.rotate_session(db, request=request, user_id=user.id, response=response, redis_client=redis_client)
    print(user.username, "님이 로그인하셨습니다.")
    return { "ok": True }
