from repositories.category.rep_category import *
from db.conn_db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.m_category import Category
from schemas.sc_category import CategoryIn



async def svc_get_all_categories(db: AsyncSession):
    return await rep_get_all_categories(db)

async def svc_get_category_by_id(db: AsyncSession, category_id: int):
    return await rep_get_category_by_id(db, category_id)

async def svc_get_category_by_name(db: AsyncSession, category_name: str):
    return await rep_get_category_by_name(db, category_name)

async def svc_get_category_by_products_id(db: AsyncSession, category_id: int) -> bool:
    return await rep_get_category_by_products_id(db, category_id)


async def svc_create_category(db: AsyncSession, category: CategoryIn):
    new_category = await rep_create_category(db, **category.model_dump())
    try:
        await db.commit()
    except ValueError as e:
        raise ValueError("카테고리 생성에 실패했습니다.")
    await db.refresh(new_category)
    return new_category

async def svc_update_category(db: AsyncSession, category_id: int, category: CategoryIn):
    updated_category = await rep_update_category(db, category_id, **category.model_dump())
    await db.commit()
    await db.refresh(updated_category)
    return updated_category


async def svc_delete_category(db: AsyncSession, category_id: int):
    deleted_category = await rep_delete_category(db, category_id)
    await db.commit()
    return deleted_category