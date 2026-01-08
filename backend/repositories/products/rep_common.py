from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.m_products import Products
from typing import Optional


async def rep_get_all_products(db: AsyncSession, category_id: int) -> list[Products]:
    result = await db.execute(select(Products).where(Products.category_id == category_id))
    return result.scalars().all()

async def rep_get_product_detail_by_id(db: AsyncSession, product_id: int) -> Optional[Products]:
    result = await db.execute(select(Products).where(Products.id == product_id))
    return result.scalar_one_or_none()
    

async def rep_get_products_paginated(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[Products]:
    result = await db.execute(
        select(Products)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def rep_create_product(db: AsyncSession, **data) -> Products:
    product = Products(**data)
    db.add(product)
    return product


async def rep_update_product(db: AsyncSession, product: Products, **data) -> Products:
    for key, value in data.items():
        if hasattr(product, key):
            setattr(product, key, value)
    return product


async def rep_delete_product(db: AsyncSession, product: Products) -> None:
    await db.delete(product)


async def rep_count_products_by_category(db: AsyncSession, category_id: int) -> int:
    from sqlalchemy import func
    result = await db.execute(select(func.count(Products.id)).where(Products.category_id == category_id))
    return result.scalar_one()
