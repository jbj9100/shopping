from fastapi import APIRouter, Depends, HTTPException, Response
from schemas.sc_user import LoginIn
from sqlalchemy.ext.asyncio import AsyncSession
from db.conn_db import get_session
from db.conn_redis import get_redis
from core.auth import auth_login
from core.auth.jwt_validator import create_access_token, create_refresh_token
from jose import jwt
import secrets
import os

router = APIRouter(prefix="/api/shop/login", tags=["login"])

# 환경변수 로드
CSRF_TOKEN_EXPIRE_SECONDS = int(os.getenv("CSRF_TOKEN_EXPIRE_SECONDS", "3600"))
REFRESH_COOKIE_NAME = os.getenv("REFRESH_COOKIE_NAME", "refresh_token")
REFRESH_COOKIE_MAX_AGE = int(os.getenv("REFRESH_COOKIE_MAX_AGE", "604800"))
REFRESH_COOKIE_HTTPONLY = os.getenv("REFRESH_COOKIE_HTTPONLY", "true").lower() == "true"
REFRESH_COOKIE_SECURE = os.getenv("REFRESH_COOKIE_SECURE", "false").lower() == "true"
REFRESH_COOKIE_SAMESITE = os.getenv("REFRESH_COOKIE_SAMESITE", "lax")
REFRESH_COOKIE_PATH = os.getenv("REFRESH_COOKIE_PATH", "/")

@router.get("/")
def login_get():
    return {"message": "login page"}

@router.post("/")
async def login(
    login_in: LoginIn,
    response: Response,
    db: AsyncSession = Depends(get_session),
    redis_client = Depends(get_redis)
) -> dict:
    """
    로그인 API (JWT + Redis + CSRF)
    - Access Token: 짧은 TTL (5분), 메모리 저장 (Frontend)
    - Refresh Token: 긴 TTL (7일), HttpOnly Cookie + Redis (jti 기반)
    - CSRF Token: Refresh 재발급 시 검증용
    
    Args:
        login_in: 로그인 요청 데이터 (email, password)
        response: FastAPI Response (Cookie 설정용)
        redis_client: Redis 클라이언트
    
    Returns:
        {"access_token": "...", "token_type": "bearer", "csrf_token": "..."}
    """
    # 1. 사용자 인증 (이메일/비밀번호 확인)
    user = await auth_login.auth_verify(db, login_in.email, login_in.password)
    
    # 2. Access Token 생성 (jti 포함)
    access_token = create_access_token(data={
        "sub": str(user.id),
        "username": user.username,
        "email": user.email
    })
    
    # 3. Refresh Token 생성 (jti 포함)
    refresh_token = create_refresh_token(data={
        "sub": str(user.id)
    })
    
    # jti 추출(redis에 Refresh Token jti 저장용)
    payload = jwt.get_unverified_claims(refresh_token)
    refresh_jti = payload.get("jti")
    
    # 4. Redis에 Refresh Token jti 저장 (멀티 디바이스 지원)
    await redis_client.setex(
        f"refresh_token:{refresh_jti}",    # refresh 검증할때는 이게 있는지 없는지 확인
        REFRESH_COOKIE_MAX_AGE,  # 환경변수 (7일)
        str(user.id)
    )
    
    # 5. 사용자별 활성 Refresh 목록 관리 
    # refresh_token 키 → user_id 값” 구조만 있으면, user_id로 토큰들을 찾아 지우려면 Redis 전체를 뒤져야 
    # 해서(스캔) 운영상 금지/비권장이거든. 그래서 역방향 인덱스로 user_tokens:{user_id}를 둬서 “user → tokens”로 
    # 바로 지울 수 있게 만든 것
    # user_tokens:123 = {jti1, jti2, ...}
    await redis_client.sadd(f"user_tokens:{user.id}", refresh_jti)
    await redis_client.expire(f"user_tokens:{user.id}", REFRESH_COOKIE_MAX_AGE)
    
    # 6. CSRF 토큰 생성
    csrf_token = secrets.token_urlsafe(32)
    await redis_client.setex(f"csrf:{user.id}", CSRF_TOKEN_EXPIRE_SECONDS, csrf_token)  # 1시간
    
    # 7. HttpOnly Cookie로 Refresh Token 전달 (브라우저한테 전달하는것)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_COOKIE_MAX_AGE,  # 환경변수 (7일)
        httponly=True,  # JavaScript 접근 차단 (XSS 방어)
        secure=False,  # 개발 환경용 (프로덕션은 True)
        samesite="lax",  # CSRF 방어
        path="/"
    )
    
    print(f"로그인 성공: {user.username}, user_id: {user.id}")
    print(f"Refresh Token Redis 저장: refresh_token:{refresh_jti}")
    
    # 8. Access Token + CSRF Token 반환
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "csrf_token": csrf_token  # Frontend가 /refresh 시 사용
    }
