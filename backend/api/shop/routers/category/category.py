from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.conn_db import get_session
from core.deps.dep_jwt_rule import require_admin
from models.m_user import Users
from schemas.sc_category import CategoryIn, CategoryOut
from services.category.svc_category import (
    svc_get_all_categories,
    svc_get_category_by_id,
    svc_create_category,
    svc_update_category,
    svc_delete_category,
    svc_get_category_by_products_id,
)

router = APIRouter(prefix="/api/shop/categories", tags=["categories"])


# 전체 조회
@router.get("/all", response_model=list[CategoryOut])
async def all_categories_list(
    db: AsyncSession = Depends(get_session)):
    try:
        return await svc_get_all_categories(db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# id로 조회
@router.get("/{category_id}", response_model=CategoryOut)
async def category_info(
    category_id: int,
    db: AsyncSession = Depends(get_session)):
    return await svc_get_category_by_id(db, category_id)

# 생성이므로 id는 필요없음
@router.post("/", response_model=CategoryOut)
async def create_category_endpoint(
    category: CategoryIn,
    db: AsyncSession = Depends(get_session),
    current_user: Users = Depends(require_admin)):
    try:
        new_category = await svc_create_category(db, category)
        return new_category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# id로 수정
@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category_endpoint(
    category_id: int,
    category: CategoryIn,
    db: AsyncSession = Depends(get_session),
    current_user: Users = Depends(require_admin)):
    try:
        categories = await svc_update_category(db, category_id, category)
        return categories
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# id로 삭제
@router.delete("/{category_id}")
async def delete_category_endpoint(
    category_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: Users = Depends(require_admin)):
    try:
        category_exists = await svc_get_category_by_products_id(db, category_id)
        if category_exists:
            raise ValueError("제품이 존재합니다, 제품 삭제후 카테고리를 삭제해 주세요.")
        category = await svc_delete_category(db, category_id)
        return {"message": category.name + " 카테고리가 삭제되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


