from fastapi import APIRouter, Request, Depends, HTTPException, Header
from fastapi.security import HTTPBearer
from db.conn_redis import get_redis
from core.auth.jwt_validator import create_access_token, verify_token, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
import secrets
import os

router = APIRouter(prefix="/api/shop/refresh", tags=["refresh"])

# 환경변수 로드
CSRF_TOKEN_EXPIRE_SECONDS = int(os.getenv("CSRF_TOKEN_EXPIRE_SECONDS", "3600"))


@router.post("/")
async def refresh_access_token(
    request: Request,
    csrf_token: str = Header(None, alias="X-CSRF-Token"),
    redis_client = Depends(get_redis)
):
    """
    Access Token 재발급 API
    - Refresh Token (HttpOnly Cookie)으로 새 Access Token 발급
    - CSRF Token 검증 포함
    
    Args:
        request: FastAPI Request (Cookie에서 Refresh Token 추출)
        csrf_token: CSRF 토큰 (헤더)
        redis_client: Redis 클라이언트
    
    Returns:
        {"access_token": "...", "token_type": "bearer"}
    """
    # 1. Cookie에서 Refresh Token 추출
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    try:
        # 2. Refresh Token 검증 (서명 검증)
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,  # jwt_validator.py에서 import
            algorithms=[ALGORITHM]
        )
        
        # 3. Type 확인
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        refresh_jti = payload.get("jti")
        
        if not user_id or not refresh_jti:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # 4. Redis에서 Refresh Token jti 확인
        stored_user_id = await redis_client.get(f"refresh_token:{refresh_jti}")
        if not stored_user_id or stored_user_id.decode() != user_id:
            raise HTTPException(status_code=401, detail="Refresh token not found or invalid")
        
        # 5. CSRF Token 검증
        stored_csrf = await redis_client.get(f"csrf:{user_id}")
        if not stored_csrf or csrf_token != stored_csrf.decode():
            raise HTTPException(status_code=403, detail="CSRF token mismatch")
        
        # 6. 새 Access Token 생성
        new_access_token = create_access_token(data={
            "sub": user_id,
        })
        
        # 7. 새 CSRF Token 생성 (회전)
        new_csrf_token = secrets.token_urlsafe(32)
        await redis_client.setex(f"csrf:{user_id}", CSRF_TOKEN_EXPIRE_SECONDS, new_csrf_token)  # 환경변수
        
        print(f"Access Token 재발급 성공: user_id={user_id}")
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "csrf_token": new_csrf_token
        }
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid refresh token: {str(e)}")
