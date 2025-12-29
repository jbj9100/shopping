from fastapi import APIRouter,Request, HTTPException, Depends , Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_conn import get_session
from db.redis_conn import get_redis
from services.svc_session import SessionService

router = APIRouter(prefix="/api/shop/logout", tags=["logout"])


@router.post("/")
async def logout(request: Request, response: Response,
                 db: AsyncSession = Depends(get_session),
                 redis_client = Depends(get_redis)):
    svc_session = SessionService()
    await svc_session.delete_session(db, request=request, response=response, redis_client=redis_client)  # 쿠키 삭제한 응답객체를 전달
    print("로그아웃 성공")
    return {"성공적으로 로그아웃되었습니다."}