from .auth_password_hash import verify_password
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.m_user import User
from sqlalchemy import select
from repositories.user.rep_user_table import get_user_by_email

async def auth_verify(session: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(session, email)
    if not user:
        raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS(User)")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS(Password)")
    return user