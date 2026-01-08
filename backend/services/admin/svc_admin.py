from sqlalchemy.ext.asyncio import AsyncSession
from db.conn_db import AsyncSessionLocal
from core.auth.auth_password_hash import hash_password
from repositories.users.rep_admin import (
    create_user, get_all_users, update_user_role, delete_user
)
from repositories.users.rep_common import get_user_by_email
from models.m_user import User
from os import getenv
from typing import Optional

async def create_admin():
    async with AsyncSessionLocal() as db:
        email = getenv("ADMIN_EMAIL")
        username = getenv("ADMIN_USERNAME")
        password = getenv("ADMIN_PASSWORD")
        role = getenv("ADMIN_ROLE")

        existing = await get_user_by_email(db, email)
        
        if existing:
            print(f"{email} is exists")
            return
        
        user = await create_user(db, username, email, hash_password(password), role)
        await db.commit()
        print(f"Admin created: {user.email}")



async def get_users_list(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    return await get_all_users(db, skip, limit)



async def change_user_role(db: AsyncSession, user_id: int, new_role: str) -> Optional[User]:

    if new_role not in ["admin", "normal-user"]:
        raise ValueError("Role은 'admin' 또는 'normal-user'만 가능합니다.")
    
    user = await update_user_role(db, user_id, new_role)
    if user:
        await db.commit()
    return user


async def remove_user(db: AsyncSession, user_id: int) -> bool:
    success = await delete_user(db, user_id)
    if success:
        await db.commit()
    return success