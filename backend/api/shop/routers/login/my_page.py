from fastapi import APIRouter, Depends
from schemas.sc_user import UserUpdateIn
from repositories.users.rep_common import get_user_by_email 
from services.login.svc_mypage import change_name, change_password
from db.conn_db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps.dep_session_rule import require_user


router = APIRouter(prefix="/api/shop/my_page", tags=["my_page"])


@router.get("/")
async def get_mypage(
                     user=Depends(require_user),
                     db: AsyncSession = Depends(get_session)):
    current_user = await get_user_by_email(db, user.email)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role,
        "created_at": current_user.created_at
    }

@router.put("/")
async def change_mypage(user_update_in: UserUpdateIn,
                        user=Depends(require_user),
                        db: AsyncSession = Depends(get_session)):
    name = None
    password = None
    
    if user_update_in.username:
        name = await change_name(db, user.id, user_update_in.username) 
    if user_update_in.password:
        password = await change_password(db, user.id, user_update_in.password)

    return {"ok": True, "name": name, "password": password}