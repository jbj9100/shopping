from fastapi import APIRouter, Request, Depends
from schemas.sc_user import UserUpdateIn
from repositories.user.rep_user import update_user
from db.conn_db import get_session
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/api/shop/my_page", tags=["my_page"])


@router.get("/me")
async def who_login(request: Request, db: AsyncSession = Depends(get_session)) -> dict:
    try:
        username = await DB_get_by_user(db, request)
        return { "username": username }
    except:
        return { "username": None }

@router.get("/")
async def get_mypage(user_update_in: UserUpdateIn, request: Request, db: AsyncSession = Depends(get_session)) -> dict:

@router.post("/")
async def verify_mypage(user_update_in: UserUpdateIn, request: Request, db: AsyncSession = Depends(get_session)):
    user = await update_user(db, user_update_in)
    return { "message": "create user" }

@router.put("/")
async def update_mypage(user_update_in: UserUpdateIn, request: Request, db: AsyncSession = Depends(get_session)):
    user = await update_user(db, user_update_in)
    return { "message": "update user" }