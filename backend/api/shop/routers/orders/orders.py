from fastapi import APIRouter, Request, Response



router = APIRouter(prefix="/api/shop/orders", tags=["orders"])


@router.get("/")
def orders_get():
    return {"message": "orders page"}