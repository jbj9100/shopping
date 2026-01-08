from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.conn_db import get_session
from core.deps.dep_session_rule import require_admin
from models.m_user import User
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
    current_user: User = Depends(require_admin)):
    try:
        new_category = await svc_create_category(db, category)
        return {"message": new_category.name + " 카테고리가 생성되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# id로 수정
@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category_endpoint(
    category_id: int,
    category: CategoryIn,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)):
    try:
        category = await svc_update_category(db, category_id, category.dict(exclude_unset=True))
        return {"message": category.name + " 카테고리가 수정되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# id로 삭제
@router.delete("/{category_id}")
async def delete_category_endpoint(
    category_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)):
    try:
        category_exists = await svc_get_category_by_products_id(db, category_id)
        if category_exists:
            raise ValueError("제품이 존재합니다, 제품 삭제후 카테고리를 삭제해 주세요.")
        category = await svc_delete_category(db, category_id)
        return {"message": category.name + " 카테고리가 삭제되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# 이미지 업로드
@router.post("/images/upload")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    product_id: Optional[int] = None,
    current_user: User = Depends(require_admin)):
    minio = get_minio(request)
    try:
        result = await upload_image_and_get_url(minio, file, product_id=product_id)
        return {"url": result.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await file.close()
