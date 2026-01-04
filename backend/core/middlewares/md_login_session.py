from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from services.redis.redis_session_context import resolve_session

class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        cookie_name: str = "sid",
        path: str = "/",
        secure: bool = True, # main.py 설정에 따라감
        **kwargs # 기타 인자 무시 (ttl, httponly 등은 Cookie 설정 시 사용되지만 여기선 DeleteCookie용)
    ):
        super().__init__(app)
        self.cookie_name = cookie_name
        self.path = path

    async def dispatch(self, request: Request, call_next):
        sid = request.cookies.get(self.cookie_name)
        print("sid_value", sid)
        request.state.auth = None # 초기화
        
        # 세션 조회 (Redis -> DB Logic)
        try:
            session_ctx = await resolve_session(sid)
        except Exception as e:
            print(f"Session resolve error: {e}")
            session_ctx = None

        if session_ctx:
            request.state.auth = session_ctx
            print("request.state.auth", request.state.auth)
        else:
            # 쿠키는 있지만 세션이 무효한 경우에만 삭제 여부 판단
            # 여기서는 sid가 있는데 resolve 실패하면 무효로 간주하고 삭제 마킹
            pass 

        response: Response = await call_next(request)

        # sid가 있었는데 검증 실패했으면 쿠키 삭제
        if sid and request.state.auth is None:
            response.delete_cookie(key=self.cookie_name, path=self.path)

        return response