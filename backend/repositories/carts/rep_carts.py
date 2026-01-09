from models.m_carts import Carts, CartItems
from models.m_products import Products
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

# 사용자 장바구니 조회
async def rep_get_cart_by_user_id(db: AsyncSession, user_id: int):
    stmt = select(Carts).where(Carts.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 장바구니 생성
async def rep_create_cart(db: AsyncSession, user_id: int):
    cart = Carts(user_id=user_id)
    db.add(cart)
    await db.flush()
    return cart



# 장바구니에 있는 모든 상품 조회
async def rep_get_cartItems_with_all_products(db: AsyncSession, cart_id: int):
    """N+1 쿼리 방지를 위해 Product JOIN"""
    stmt = (
        select(CartItems, Products)
        .join(Products, CartItems.product_id == Products.id)
        .where(CartItems.cart_id == cart_id)
        .order_by(CartItems.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.all()  # 결과: [(아이템1, 제품1), (아이템2, 제품2), (아이템3, 제품3)]

# 장바구니에서 특정 아이템 조회 (product_id 기준)
async def rep_get_cartItems_with_product(db: AsyncSession, cart_id: int, product_id: int):
    result = await db.execute(select(CartItems).filter(CartItems.cart_id == cart_id, CartItems.product_id == product_id))
    return result.scalar_one_or_none()

# 장바구니에서 특정 아이템 조회 (cartItem_id 기준)
async def rep_get_cartItem_by_id(db: AsyncSession, cartItem_id: int):
    result = await db.execute(select(CartItems).filter(CartItems.id == cartItem_id))
    return result.scalar_one_or_none()  

# 장바구니에 아이템 추가
async def rep_add_cartItems(db: AsyncSession, cart_id: int, product_id: int, quantity: int):
    cart_item = CartItems(
        cart_id=cart_id,
        product_id=product_id,
        quantity=quantity
    )
    db.add(cart_item)
    await db.flush()
    return cart_item

# 장바구니에서 아이템 수량 변경
async def rep_update_cartItems_quantity(db: AsyncSession, cart_id, product_id, quantity):
    result = await rep_get_cartItems_with_details(db, cart_id, product_id)
    result.quantity = quantity
    db.add(result)
    return result

# 장바구니에서 아이템 삭제
async def rep_delete_cartItems(db: AsyncSession, cart_id, product_id):
    result = await rep_get_cartItems_with_product(db, cart_id, product_id)
    if result:
        db.delete(result)
    return result

# 장바구니 전체 비우기
async def rep_clear_cartItems(db: AsyncSession, cart_id):
    result = await db.execute(select(CartItems).filter(CartItems.cart_id == cart_id))
    items = result.scalars().all()
    for item in items:
        await db.delete(item)
    return items