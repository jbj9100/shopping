from models.m_orders import Orders, OrderItems
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from schemas.sc_orders import OrderCreateIn
from schemas.sc_carts import CartItemsOut
from models.m_user import Users



async def rep_create_order(db: AsyncSession, users: Users, order_create_in: OrderCreateIn, cartItems: CartItemsOut, order_number: str):
    shipping_fee = 0
    items_amount = cartItems.total_price
    total_amount = items_amount + shipping_fee
    
    order = Orders(
        user_id=users.id,
        order_number=order_number,
        items_amount=items_amount,
        total_amount=total_amount,
        shipping_fee=shipping_fee,
        shipping_address=order_create_in.shipping_address,
    )
    db.add(order)
    await db.flush()
    
    for cart_item in cartItems.items:
        order_item = OrderItems(
            order_id=order.id,
            product_id=cart_item.product_id,
            name_snapshot=cart_item.product_name,
            price_snapshot=cart_item.discount_price,
            quantity=cart_item.quantity,
        )
        db.add(order_item)
    
    return order


async def rep_all_orders(db: AsyncSession, users: Users):
    """사용자의 모든 주문을 조회 (OrderItems 포함)"""
    result = await db.execute(
        select(Orders)
        .where(Orders.user_id == users.id)
        .options(selectinload(Orders.items))
        .order_by(Orders.created_at.desc())
    )
    return result.scalars().all()


async def rep_order_detail(db: AsyncSession, order_id: int, users: Users):
    """특정 주문 상세 조회 (OrderItems 포함, 권한 검증)"""
    result = await db.execute(
        select(Orders)
        .where(Orders.id == order_id, Orders.user_id == users.id)
        .options(selectinload(Orders.items))
    )
    return result.scalar_one_or_none()