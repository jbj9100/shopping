from fastapi import Request, status, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.m_user import Users
from core.auth.jwt_validator import verify_token
from db.conn_db import get_session
from db.conn_redis import get_redis

security = HTTPBearer()


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security), # 헤더에서 읽기
    db: AsyncSession = Depends(get_session),
    redis_client = Depends(get_redis)
) -> Users:
    """
    JWT Bearer 토큰에서 사용자 정보 추출 및 DB 조회
    (jti 블랙리스트 체크 포함)
    
    Args:
        credentials: HTTP Bearer 토큰
        db: DB 세션
        redis_client: Redis 클라이언트 (블랙리스트 체크용)
    
    Returns:
        Users 객체
    
    Raises:
        HTTPException: 토큰이 유효하지 않거나 사용자를 찾을 수 없는 경우
    """
    token = credentials.credentials # Authorization에서 Bearer 제외한 토큰 값 추출 (ex) "eyJhbGci...")
    payload = await verify_token(token, redis_client)  # JWT 검증 + 블랙리스트 체크해서 payload 반환
    
    # JWT payload에서 user_id 추출
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload (missing 'sub')"
        )
    
    # DB에서 사용자 조회
    result = await db.execute(select(Users).where(Users.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


# 기존 이름 유지 (require_user)
async def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_session),
    redis_client = Depends(get_redis)
) -> Users:
    """
    로그인한 사용자 확인 (JWT 기반)
    기존 Session 기반 require_user와 동일한 역할
    
    Returns:
        Users 객체
    """
    return await get_current_user_from_token(credentials, db, redis_client)


# 기존 이름 유지 (require_admin)
async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_session),
    redis_client = Depends(get_redis)
) -> Users:
    """
    관리자 권한 확인 (JWT 기반)
    기존 Session 기반 require_admin과 동일한 역할
    
    Returns:
        Users 객체 (admin만)
    
    Raises:
        HTTPException: 관리자 권한이 없는 경우
    """
    user = await get_current_user_from_token(credentials, db, redis_client)
    
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin 권한이 필요합니다."
        )
    
    return user
