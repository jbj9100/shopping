from fastapi import APIRouter, Request, Depends, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.conn_redis import get_redis
from core.auth.jwt_validator import revoke_access_token
from core.deps.dep_jwt_rule import require_user
from models.m_user import Users
from jose import jwt

router = APIRouter(prefix="/api/shop/logout", tags=["logout"])
security = HTTPBearer()


@router.post("/")
async def logout(
    request: Request,
    user: Users = Depends(require_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis_client = Depends(get_redis),
    response: Response = None
):
    """
    로그아웃 API (JWT + Redis)
    - Access Token: jti 블랙리스트 추가 (즉시 무효화)
    - Refresh Token: jti 기반 삭제 (재발급 불가)
    
    Args:
        request: FastAPI Request (Cookie 추출용)
        user: 현재 로그인한 사용자 (require_user에서 추출)
        credentials: Access Token
        redis_client: Redis 클라이언트
        response: FastAPI Response (Cookie 삭제용)
    
    Returns:
        성공 메시지
    """
    # 1. Access Token을 jti 블랙리스트에 추가
    access_token = credentials.credentials
    await revoke_access_token(access_token, redis_client)
    
    # 2. Refresh Token에서 jti 추출
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload = jwt.get_unverified_claims(refresh_token)
            refresh_jti = payload.get("jti")
            
            # 3. Redis에서 Refresh Token jti 삭제
            if refresh_jti:
                await redis_client.delete(f"refresh_token:{refresh_jti}")
                await redis_client.srem(f"user_tokens:{user.id}", refresh_jti)
                print(f"Redis 삭제: refresh_token:{refresh_jti}")
        except Exception as e:
            print(f"Refresh Token 파싱 실패: {e}")
    
    # 4. Refresh Token Cookie 삭제
    if response:
        response.delete_cookie(key="refresh_token", path="/")
    
    print(f"로그아웃 성공: user_id={user.id}")
    
    return {"message": "성공적으로 로그아웃되었습니다."}
