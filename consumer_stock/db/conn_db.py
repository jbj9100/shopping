import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from typing import AsyncGenerator
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# 환경변수에서 DB 연결 문자열 가져오기
DATABASE_CONN = os.getenv("DATABASE_CONN", "")
if not DATABASE_CONN:
    raise ValueError("DATABASE_CONN 환경변수가 설정되지 않았습니다")

# 비동기 엔진 생성
engine = create_async_engine(
    DATABASE_CONN,
    echo=False,  # SQL 로그 출력 (개발 시 True로 변경)
    pool_pre_ping=True,  # 연결 유효성 자동 체크
    pool_size=10,
    max_overflow=0,
    pool_recycle=300
)

# ORM은 "Connection" 대신 "Session"을 씁니다.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # async에서 흔히 끔
    autoflush=False,
    autocommit=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if engine is None:
        raise Exception("Database engine not initialized")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError:
            # 세션 내부 에러면 rollback은 해주는게 안전
            await session.rollback()
            raise


# Consumer main.py에서 사용하는 함수명
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """get_session의 별칭 (Consumer에서 사용)"""
    async for session in get_session():
        yield session


async def ping_db() -> tuple[bool, str | None]:
    """
    데이터베이스 연결 테스트
    
    Returns:
        (성공 여부, 에러 메시지 또는 None)
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True, None
    except SQLAlchemyError as e:
        return False, f"Database connection error: {str(e)}"


async def dispose_engine() -> None:
    await engine.dispose()
