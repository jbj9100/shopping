from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from schemas.sc_products import ProductIn, ProductOut
from repositories.products.rep_common import (
    rep_get_all_products, 
    rep_get_product_detail_by_id, 
    rep_create_product,
    rep_update_product,
    rep_delete_product,
    rep_increment_view_count
)
from repositories.products.rep_filter import rep_filter_products


async def svc_get_all_products(db: AsyncSession, category_id: Optional[int] = None):
    if category_id:
        # 카테고리별 조회
        products = await rep_get_all_products(db, category_id)
    else:
        # 전체 조회
        products = await rep_filter_products(db)
    return products


async def svc_get_product_by_id(db: AsyncSession, product_id: int):
    """상품 상세 조회 (조회수 자동 증가)"""
    product = await rep_get_product_detail_by_id(db, product_id)
    if not product:
        raise ValueError("제품을 찾을 수 없습니다.")
    
    # 조회수 증가
    await rep_increment_view_count(db, product)
    await db.commit()
    await db.refresh(product)
    
    return product


async def svc_create_product(db: AsyncSession, product: ProductIn):
    new_product = await rep_create_product(db, **product.model_dump())
    try:
        await db.commit()
    except ValueError as e:
        raise ValueError("제품 생성에 실패했습니다.")
    await db.refresh(new_product)
    return new_product


async def svc_update_product(db: AsyncSession, product_id: int, product: ProductIn):
    existing = await rep_get_product_detail_by_id(db, product_id)
    if not existing:
        raise ValueError("제품을 찾을 수 없습니다.")
    updated = await rep_update_product(db, existing, **product.model_dump(exclude_unset=True))
    try:
        await db.commit()
    except ValueError as e:
        raise ValueError("제품 수정에 실패했습니다.")
    await db.refresh(updated)
    return updated



async def svc_delete_product(db: AsyncSession, product_id: int):
    product = await rep_get_product_detail_by_id(db, product_id)
    if not product:
        raise ValueError("제품을 찾을 수 없습니다.")
    await rep_delete_product(db, product)
    try:
        await db.commit()
    except ValueError as e:
        raise ValueError("제품 삭제에 실패했습니다.")
    return product


async def svc_get_products_stock(db: AsyncSession, product_id: int) -> int:
    product = await rep_get_product_detail_by_id(db, product_id)
    if not product:
        raise ValueError("제품을 찾을 수 없습니다.")
    if product.stock < 0:
        raise ValueError("제품 재고가 부족합니다.")
    return product.stock

async def svc_update_product_stock(db: AsyncSession, product_id: int, stock: int):
    product = await rep_get_product_detail_by_id(db, product_id)
    if not product:
        raise ValueError("제품을 찾을 수 없습니다.")
    if stock < 0:
        raise ValueError("제품 재고가 부족합니다.")
    product.stock = stock
    await db.commit()
    return product