from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.m_user import User
from typing import Optional


async def create_user(db: AsyncSession, username: str, email: str, password_hash: str, role: str = "normal-user") -> User:
    """새 사용자 생성 (DB에 add만, commit은 Service에서)"""
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role=role
    )
    db.add(user)
    return user


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    return result.scalars().all()

async def update_user_role(db: AsyncSession, user_id: int, new_role: str) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if user:
        user.role = new_role
        return user
    return None

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    if user:
        await db.delete(user)
        return True
    return False