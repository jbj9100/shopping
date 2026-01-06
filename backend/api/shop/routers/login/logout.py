from fastapi import APIRouter,Request, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from db.conn_db import get_session
from db.conn_redis import get_redis
from services.cookie.svc_session import delete_session
from services.cookie.svc_cookie_setting import cookie_settings

router = APIRouter(prefix="/api/shop/logout", tags=["logout"])


@router.post("/")
async def logout(request: Request, response: Response,
                 db: AsyncSession = Depends(get_session),
                 redis_client = Depends(get_redis)):
    old_sid = request.cookies.get(cookie_settings.COOKIE_NAME)
    await delete_session(db, old_sid=old_sid, redis_client=redis_client)  # 쿠키 삭제한 응답객체를 전달
    response.delete_cookie(key=cookie_settings.COOKIE_NAME)
    print("쿠키 삭제 성공")
    return {"성공적으로 로그아웃되었습니다."}