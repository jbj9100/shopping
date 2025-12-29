from fastapi import Request, status, HTTPException
from models.user import User
from core.redis_session_context import SessionContext
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

# 로그인한 세션이고, 그 세션의 user의 role이 allowed_roles에 있는지
def require_role(*allowed_roles: str) -> Callable[[Request], User]:
    allowed = set(allowed_roles)

    def _dep(request: Request) -> User:
        user = require_user(request)
        # SessionContext.user는 ORM 객체이거나 단순 객체일 수 있음. role 속성 접근
        role = getattr(user, "role", None)
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden (role required: {sorted(allowed)}).",
            )
        return user

    return _dep

