from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
import uuid
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-for-development-only")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "5"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def create_access_token(data: dict) -> str:
    """
    JWT Access Token 생성 (짧은 TTL)
    
    Args:
        data: JWT payload에 포함될 데이터 (예: {"sub": "user_id", "username": "..."})
    
    Returns:
        인코딩된 JWT 문자열
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # jti 추가 (블랙리스트용)
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())  # Token ID
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    JWT Refresh Token 생성 (긴 TTL)
    
    Args:
        data: JWT payload (최소한 sub만)
    
    Returns:
        Refresh Token 문자열
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # jti 추가 (멀티 디바이스 지원)
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid.uuid4())  # Refresh Token ID
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(token: str, redis_client=None) -> dict:
    """
    JWT 토큰 검증 및 디코딩 (jti 블랙리스트 체크 포함)
    
    Args:
        token: JWT 문자열
        redis_client: Redis 클라이언트 (블랙리스트 체크용)
    
    Returns:
        디코딩된 payload (dict)
    
    Raises:
        HTTPException: 토큰이 유효하지 않을 경우
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # jti 블랙리스트 확인 (Redis)
        if redis_client:
            jti = payload.get("jti")
            if jti and await redis_client.exists(f"jwt:revoked:{jti}"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def revoke_access_token(token: str, redis_client) -> None:
    """
    Access Token을 블랙리스트에 추가 (즉시 로그아웃)
    
    Args:
        token: JWT 문자열
        redis_client: Redis 클라이언트
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        if jti and exp:
            # 남은 만료시간만큼 TTL 설정
            ttl = int(exp - datetime.utcnow().timestamp())
            if ttl > 0:
                await redis_client.setex(f"jwt:revoked:{jti}", ttl, "1")
    except JWTError:
        pass  # 이미 만료된 토큰은 무시

