from fastapi import APIRouter
from schemas.sc_user import Signup
from models.m_user import User
from core.auth.auth_password_hash import hash_password
from db.conn_db import get_session
from services.login.svc_signup import signup_user
from fastapi import HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/shop/signup", tags=["signup"])  


@router.get("/")
def signup_get():
    return "signup"

@router.post("/")
async def signup_post(signup: Signup, session: AsyncSession = Depends(get_session)):
    try:
        user = await signup_user(session, signup)
        return {"ok": True, "id": user.id, "username": user.username, "email": user.email}
    except HTTPException as e:
        if e.detail == "USERNAME_EXISTS":
            raise HTTPException(status_code=400, detail="username already exists")
        if e.detail == "EMAIL_EXISTS":
            raise HTTPException(status_code=400, detail="email already exists")
        raise HTTPException(status_code=400, detail=e.detail)