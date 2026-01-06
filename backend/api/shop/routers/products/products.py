from fastapi import APIRouter, Request, Response, UploadFile, File 
from typing import Optional 
from core.deps.dep_session_rule import require_admin
from db.conn_db import get_session
from schemas.sc_products import ProductOut
from models.m_user import User
from fastapi import HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/api/shop/products", tags=["products"])


@router.get("/")
def products_get():
    return {"message": "상품 목록 조회"}


@router.get("/{product_id}", response_model=ProductOut)
async def product_get_id(
        product_id: int,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(require_admin) 
):
    # 상품 생성 로직
    pass       

@router.post("/")
async def product_create(
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(require_admin) 
):
    # 상품 생성 로직
    pass       

@router.put("/{product_id}")
async def product_update(
        product_id: int,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(require_admin) 
):
    # 상품 생성 로직
    pass       

@router.delete("/{product_id}")
async def product_delete(
        product_id: int,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(require_admin) 
):
    # 상품 생성 로직
    pass       


@router.post("/images/upload")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    product_id: Optional[int] = None,
):
    minio = get_minio(request)
    try:
        result = await upload_image_and_get_url(minio, file, product_id=product_id)
        return {"url": result.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await file.close()

