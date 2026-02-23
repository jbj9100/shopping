from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from services.admin.svc_admin import get_users_list, change_user_role, remove_user, remove_users_bulk
from db.conn_db import get_session
from models.m_user import Users
from core.deps.dep_jwt_rule import require_admin


router = APIRouter(prefix="/api/shop/admin", tags=["admin"])


@router.get("/")
async def admin_get(
    db: AsyncSession = Depends(get_session),
    current_user: Users = Depends(require_admin)
):
    users = await get_users_list(db)
    return {"users": users}

    
@router.put("/")
async def admin_put(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user: Users = Depends(require_admin)
):
    data = await request.json()
    user_id = data.get("user_id")
    role = data.get("role")
    await change_user_role(db, user_id, role)
    return {"message": "updated"}


@router.delete("/")
async def admin_delete(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user: Users = Depends(require_admin)
):
    data = await request.json()
    user_id = data.get("user_id")
    await remove_user(db, user_id)
    return {"message": "deleted"}


@router.post("/bulk-delete")
async def admin_bulk_delete(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user: Users = Depends(require_admin)
):
    data = await request.json()
    user_ids = data.get("user_ids", [])
    
    if not user_ids:
        return {"message": "No user IDs provided", "deleted_count": 0}
    
    result = await remove_users_bulk(db, user_ids)
    return {
        "message": "bulk delete completed",
        "deleted_count": result["deleted_count"],
        "failed_ids": result["failed_ids"]
    }
