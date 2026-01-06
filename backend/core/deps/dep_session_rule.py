from fastapi import Request, status, HTTPException
from models.m_user import User
from services.redis.redis_session_context import SessionContext
from typing import Callable

# getattr(객체, "속성이름", 기본값) 
# -> 객체에 그 속성이 있으면 값을 가져오고 없으면 기본값을 반환하는 안전장치
#    속성 차체가 없는경우에 AttributeError를 발생시키니까 없어도 안전하게 None으로 처리하는것

# request.state.session 이 있는 상태 있는지 없는지 체크
def require_session(request: Request) -> SessionContext:
    # Middleware에서 넣어준 state.auth 사용
    sess = getattr(request.state, "auth", None)
    if sess is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated (session not found).",
        )
    return sess


# 로그인한 user가 있는지 ( user_id와 user가 있는지)
def require_user(request: Request) -> User:
    sess = require_session(request)
    # SessionContext에는 user_id와 user가 항상 세팅되어 있음 (user가 None이면 resolve_session이 반환을 안하므로)
    
    if sess.user is None:
        # 혹시 모르니 방어 코드
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated (user missing context).",
        )
    return sess.user


# Admin 전용 간편 함수
def require_admin(request: Request) -> User:
    """현재 로그인한 사용자가 admin인지 확인 request.state.auth.user.role 에서 가져옴"""
    user = require_user(request)  # 현재 로그인한 사용자 (이미 role 포함)
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin 권한이 필요합니다.",
        )
    return user
