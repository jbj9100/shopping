from fastapi import APIRouter, Request, Response



router = APIRouter(prefix="/api/shop/products", tags=["products"])


@router.get("/")
def products_get():
    return {"message": "products page"}
