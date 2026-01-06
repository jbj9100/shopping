from sqlalchemy.ext.asyncio import AsyncSession
from core.auth.auth_password_hash import hash_password
from repositories.user.rep_user_table import update_username, update_password_hash


async def change_name(db: AsyncSession, user_id: int, new_name: str) -> str:
    await update_username(db, user_id, new_name)
    await db.commit()
    return new_name


async def change_password(db: AsyncSession, user_id: int, new_password: str) -> bool:
    hashed = hash_password(new_password)
    await update_password_hash(db, user_id, hashed)
    await db.commit()
    return True
