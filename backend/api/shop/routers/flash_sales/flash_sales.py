from fastapi import APIRouter


router = APIRouter(prefix="/api/shop/flash_sale", tags=["flash_sale"])


@router.get("/")
async def get_flash_sales():
    pass
