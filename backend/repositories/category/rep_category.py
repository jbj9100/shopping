from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.m_category import Category
from models.m_products import Products
from typing import Optional


async def rep_get_all_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(
        select(Category)
        .order_by(Category.name)
    )
    return result.scalars().all()


async def rep_get_category_by_id(db: AsyncSession, category_id: int) -> Optional[Category]:
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    return result.scalar_one_or_none()

async def rep_get_category_by_name(db: AsyncSession, category_name: str) -> bool:
    result = await db.execute(
        select(Category).where(Category.name == category_name)
    )
    return result.scalar() is not None

async def rep_get_category_by_products_id(db: AsyncSession, category_id: int) -> bool:
    result = await db.execute(
        select(Products.id).where(Products.category_id == category_id).limit(1)
    )
    return result.scalar() is not None

async def rep_create_category(db: AsyncSession, **data) -> Category:
    category = Category(**data)
    db.add(category)
    return category


async def rep_update_category(db: AsyncSession, **data) -> Category:
    category = await rep_get_category_by_name(db, data["name"])
    if not category:
        raise ValueError("카테고리가 존재하지 않습니다.")
    for key, value in data.items():
        if hasattr(category, key):
            setattr(category, key, value)
    db.add(category)
    return category


async def rep_delete_category(db: AsyncSession, category_id: int) -> Category:
    category = await rep_get_category_by_id(db, category_id)
    if not category:
        raise ValueError("카테고리가 존재하지 않습니다.")
    await db.delete(category)
    return category
