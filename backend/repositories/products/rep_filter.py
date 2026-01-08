from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from models.m_products import Products
from typing import Optional


async def rep_filter_products(
    db: AsyncSession,
    category_id: Optional[int] = None,
    brands: Optional[list[str]] = None,
    free_shipping: Optional[bool] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> list[Products]:
    """상품 필터링"""
    query = select(Products)
    
    conditions = []
    
    # 카테고리 필터
    if category_id is not None:
        conditions.append(Products.category_id == category_id)
    
    # 브랜드 필터
    if brands and len(brands) > 0:
        conditions.append(Products.brand.in_(brands))
    
    # 무료배송 필터
    if free_shipping is not None:
        conditions.append(Products.free_shipping == free_shipping)
    
    # 가격 범위 필터
    if min_price is not None:
        conditions.append(Products.price >= min_price)
    if max_price is not None:
        conditions.append(Products.price <= max_price)
    
    # 조건 적용
    if conditions:
        query = query.where(and_(*conditions))
    
    # 페이징
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def rep_count_filtered_products(
    db: AsyncSession,
    category_id: Optional[int] = None,
    brands: Optional[list[str]] = None,
    free_shipping: Optional[bool] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None
) -> int:
    """필터링된 상품 개수"""
    query = select(func.count(Products.id))
    
    conditions = []
    
    if category_id is not None:
        conditions.append(Products.category_id == category_id)
    
    if brands and len(brands) > 0:
        conditions.append(Products.brand.in_(brands))
    
    if free_shipping is not None:
        conditions.append(Products.free_shipping == free_shipping)
    
    if min_price is not None:
        conditions.append(Products.price >= min_price)
    if max_price is not None:
        conditions.append(Products.price <= max_price)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    result = await db.execute(query)
    return result.scalar_one()  
