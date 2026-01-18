from fastapi import APIRouter, Request, Response, UploadFile, File, Query, Depends, HTTPException
from typing import Optional 
from core.deps.dep_jwt_rule import require_admin
from db.conn_db import get_session
from schemas.sc_products import ProductOut, ProductIn
from models.m_user import Users
from sqlalchemy.ext.asyncio import AsyncSession
from services.products.svc_products import *



router = APIRouter(prefix="/api/shop/products", tags=["products"])


# 카테고리별 전체 제품 조회
# GET /api/shop/products?category_id=1
@router.get("/", response_model=list[ProductOut])
async def products_get_all(
        category_id: Optional[int] = None,
        db: AsyncSession = Depends(get_session)):
    return await svc_get_all_products(db, category_id)

# 상세페이지 조회
@router.get("/{product_id}", response_model=ProductOut)
async def product_get_id(
        product_id: int,
        db: AsyncSession = Depends(get_session)):
    return await svc_get_product_by_id(db, product_id)

# 생성
@router.post("/", response_model=ProductOut)
async def product_create(
        product: ProductIn,
        db: AsyncSession = Depends(get_session),
        current_user: Users = Depends(require_admin)):
    new_product = await svc_create_product(db, product)   
    return {"message": f"{new_product.name} 생성되었습니다."}
      
# 수정
@router.patch("/{product_id}", response_model=ProductOut)
async def product_update(
        product_id: int,
        product: ProductIn,
        db: AsyncSession = Depends(get_session),
        current_user: Users = Depends(require_admin)):
    updated_product = await svc_update_product(db, product_id, product)
    #print(updated_product.model_validate(updated_product).model_dump())
    return updated_product

#삭제
@router.delete("/{product_id}")
async def product_delete(
        product_id: int,
        db: AsyncSession = Depends(get_session),
        current_user: Users = Depends(require_admin)):
    deleted_product = await svc_delete_product(db, product_id)
    return {"message": f"{deleted_product.name} 삭제되었습니다."}


# 필터
@router.get("/filter", response_model=list[ProductOut])
async def products_filter(
        db: AsyncSession = Depends(get_session)):
    return await svc_filter_products(db)

