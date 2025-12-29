from fastapi import APIRouter, Request




router = APIRouter(prefix="/api/carts", tags=["carts"])


@router.get("/")
def cart_get():
    return {"message": "cart page"}