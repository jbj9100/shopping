from fastapi import APIRouter, Request, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps.dep_session_rule import require_user
from db.conn_db import get_session
from schemas.sc_orders import OrderOut, OrderCreateIn
from typing import List
from services.orders.svc_orders import (
    svc_create_order,
    svc_all_orders,
    svc_order_detail
)

router = APIRouter(prefix="/api/shop/orders", tags=["orders"])



# 주문 생성 (장바구니 기반)
@router.post("/", response_model=OrderOut)
async def orders_post(
    order_create_in: OrderCreateIn,
    db: AsyncSession = Depends(get_session),
    users=Depends(require_user)):
    return await svc_create_order(db, order_create_in, users)



# 과거 모든 주문 조회
@router.get("/", response_model=List[OrderOut])
async def orders_get(
    db: AsyncSession = Depends(get_session),
    users=Depends(require_user)):
    return await svc_all_orders(db, users)


# 과거 주문 상세 조회
@router.get("/{order_id}", response_model=OrderOut)
async def orders_get(
    order_id: int,
    db: AsyncSession = Depends(get_session),
    users=Depends(require_user)):
    return await svc_order_detail(db, order_id, users)