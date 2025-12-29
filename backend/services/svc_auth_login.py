from core.password_hash import verify_password
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from sqlalchemy import select


async def auth_verify(session: AsyncSession, email: str, password: str) -> User:
    r = await session.execute(select(User).where(User.email == email))
    user = r.scalar_one_or_none()  # User(id=7, email="a@test.com", password_hash="...", ...)
    # print("user.id =", user.id)
    # print("user.email =", user.email)
    if not user:
        raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS(User)")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS(Password)")
    return user