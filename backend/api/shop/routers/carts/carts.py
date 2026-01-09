from fastapi import APIRouter, Depends
from core.deps.dep_session_rule import require_user
from db.conn_db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.sc_carts import ( 
        CartItemsOut,
        CartItemIn,
        CartUpdateQtyIn
    )
from services.carts.svc_carts import (
        svc_add_to_cartItems,
        svc_update_cartItems_quantity,
        svc_delete_cartItems,
        svc_clear_cartItems,
        svc_get_cart_with_items
    )

router = APIRouter(prefix="/api/carts", tags=["carts"])


# 장바구니 조회 (GET /api/carts)
@router.get("/", response_model=CartItemsOut)
async def cart_get(
    user=Depends(require_user),
    db: AsyncSession = Depends(get_session)) -> CartItemsOut:
    return await svc_get_cart_with_items(db, user.id)


# 상품 추가 (POST /api/carts)
@router.post("/", response_model=CartItemsOut)
async def cart_item_add(
    cartitem: CartItemIn,
    user=Depends(require_user),
    db: AsyncSession = Depends(get_session)) -> CartItemsOut:
    return await svc_add_to_cartItems(db, user.id, cartitem.product_id, cartitem.quantity)


# 수량 변경 (PATCH /api/carts/{item_id})
@router.patch("/{item_id}", response_model=CartItemsOut)
async def cart_item_update(
    item_id: int,
    update_data: CartUpdateQtyIn,
    user=Depends(require_user),
    db: AsyncSession = Depends(get_session)) -> CartItemsOut:
    return await svc_update_cartItems_quantity(db, user.id, item_id, update_data.quantity)


# 아이템 삭제 (DELETE /api/carts/{item_id})
@router.delete("/{item_id}", response_model=CartItemsOut)
async def cart_item_delete(
    item_id: int,
    user=Depends(require_user),
    db: AsyncSession = Depends(get_session)) -> CartItemsOut:
    return await svc_delete_cartItems(db, user.id, item_id)


# 전체 삭제 (DELETE /api/carts)
@router.delete("/", response_model=CartItemsOut)
async def cart_clear(
    user=Depends(require_user),
    db: AsyncSession = Depends(get_session)) -> CartItemsOut:
    return await svc_clear_cartItems(db, user.id)