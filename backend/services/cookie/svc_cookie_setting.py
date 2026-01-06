from pydantic_settings import BaseSettings

class CookieSettings(BaseSettings):
    COOKIE_NAME: str = "sid"
    COOKIE_TTL_SECONDS: int = 60 * 60 * 24 * 7  # 7일 (기본값)
    COOKIE_SECURE: bool = False
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"
    COOKIE_PATH: str = "/"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # .env의 다른 변수 무시

cookie_settings = CookieSettings()