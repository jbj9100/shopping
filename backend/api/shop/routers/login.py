from fastapi import APIRouter, Request, Response, Depends
from schemas.user import Login
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_conn import get_session
from db.redis_conn import get_redis
from services import svc_auth_login
from services.svc_session import SessionService
from repositories.rep_usersession_id_check import DB_get_by_user

router = APIRouter(prefix="/api/shop/login", tags=["login"])

@router.get("/")
def login_get():
    return {"message": "login page"}

@router.post("/")
async def login(login: Login, request: Request, response: Response,
                db: AsyncSession = Depends(get_session),
                redis_client = Depends(get_redis)) -> dict:
    user = await svc_auth_login.auth_verify(db, login.email, login.password)
    svc_session = SessionService()
    await svc_session.rotate_session(db, request=request, user_id=user.id, response=response, redis_client=redis_client)
    print(user.username, "님이 로그인하셨습니다.")
    return { "ok": True }

@router.get("/me")
async def who_login(request: Request, db: AsyncSession = Depends(get_session)) -> dict:
    try:
        username = await DB_get_by_user(db, request)
        return { "username": username }
    except:
        return { "username": None }

    
