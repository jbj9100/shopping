from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.m_user import User
from typing import Optional



# 전체 User테이블에서 모든 컬럼 가져오기
# select(User)  =  SELECT * FROM users
# user.id = 1
# user.username = "testuser"
# user.email = "test@test.com"
# user.role = "normal-user"

# User 테이블에서 username 컬럼만 가져오기
# select(User.username)  =  SELECT username FROM users
# user.username = "testuser"

# user = result.scalar_one_or_none()
# 1개 → User 객체
# 0개 → None
# 2개 이상 → 에러

# users = result.scalars().all()
# [User1, User2, User3, ...]

#--------------------------------------------------------------------
# # 1. 쿼리 준비
# query = select(User).where(User.id == 1)
#   → "SELECT * FROM users WHERE id = 1"

# 2. DB 실행 (네트워크 통신)
# result = await db.execute(query)
# 앱 → [쿼리 전송] → PostgreSQL
# 앱 ← [Result 컨테이너] ← PostgreSQL
# Result 안에는:
# {
#   "raw_data": [{"id": 1, "username": "testuser", ...}],
#   "metadata": {...}
# }

# 3. 데이터 추출 & ORM 매핑
# user = result.scalar_one_or_none()
# Result → User 객체로 변환
# user.id = 1
# user.username = "testuser"

#--------------------------------------------------------------------
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, user_id: int) -> Optional[str]:
    result = await db.execute(select(User.username).where(User.id == user_id))
    return result.scalar_one_or_none()

    
async def update_username(db: AsyncSession, user_id: int, new_username: str) -> None:
    user = await get_user_by_id(db, user_id)
    if user:
        user.username = new_username

async def update_password_hash(db: AsyncSession, user_id: int, new_password_hash: str) -> None:
    user = await get_user_by_id(db, user_id)
    if user:
        user.password_hash = new_password_hash


async def create_user(db: AsyncSession, username: str, email: str, password_hash: str) -> User:
    """새 사용자 생성 (DB에 add만, commit은 Service에서)"""
    user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )
    db.add(user)
    return user