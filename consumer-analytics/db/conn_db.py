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

# DB Pool 설정
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# 비동기 엔진 생성
engine = create_async_engine(
    DATABASE_CONN,
    echo=False,
    pool_pre_ping=True,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_recycle=DB_POOL_RECYCLE
)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
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
            await session.rollback()
            raise


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
