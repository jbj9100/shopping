from sqlalchemy.ext.asyncio import AsyncSession
from schemas.sc_carts import CartItemsOut, CartItemOut
from repositories.carts.rep_carts import (
    rep_get_cart_by_user_id, 
    rep_create_cart, 
    rep_get_cartItems_with_all_products,
    rep_get_cartItems_with_product,
    rep_get_cartItem_by_id,
    rep_add_cartItems, 
    rep_update_cartItems_quantity, 
    rep_delete_cartItems, 
    rep_clear_cartItems
)


# 장바구니 가져오기
async def svc_get_cart(db: AsyncSession, user_id: int):
    result = await rep_get_cart_by_user_id(db, user_id)
    return result


# 장바구니 생성
async def svc_create_cart(db: AsyncSession, user_id: int):
    existing_cart = await rep_get_cart_by_user_id(db, user_id)
    if existing_cart:
        raise ValueError("장바구니가 이미 존재합니다.")
    result = await rep_create_cart(db, user_id)
    await db.commit()
    await db.refresh(result)
    return result


# 장바구니 조회 (실무 표준: Pydantic 변환 포함)
async def svc_get_cart_with_items(db: AsyncSession, user_id: int):
    """CartItemsOut 형태로 반환 - Service에서 Pydantic 변환"""

    cart = await rep_get_cart_by_user_id(db, user_id)
    if not cart:
        cart = await rep_create_cart(db, user_id)
        await db.commit()
    
    items_data = await rep_get_cartItems_with_all_products(db, cart.id)
    
    cart_items = []
    for cart_item, product in items_data:
        cart_items.append(
            CartItemOut(
                id=cart_item.id,
                product_id=cart_item.product_id,
                product_name=product.name,
                product_price=product.price,
                product_image=product.image or "",
                quantity=cart_item.quantity,
            )
        )
    
    total_items = len(cart_items)
    total_price = sum(item.product_price * item.quantity for item in cart_items)
    
    return CartItemsOut(
        items=cart_items,
        total_items=total_items,
        total_price=total_price
    )


# 장바구니에 추가 (중복 상품은 수량 증가)
async def svc_add_to_cartItems(db: AsyncSession, user_id: int, product_id: int, quantity: int):
    """상품을 장바구니에 추가하고 업데이트된 전체 장바구니를 반환"""
    cart = await rep_get_cart_by_user_id(db, user_id)
    if not cart:
        cart = await rep_create_cart(db, user_id)
        await db.commit()
    
    existing_item = await rep_get_cartItems_with_product(db, cart.id, product_id)
    
    if existing_item:
        existing_item.quantity += quantity
        await db.commit()
    else:
        await rep_add_cartItems(db, cart.id, product_id, quantity)
        await db.commit()
    
    return await svc_get_cart_with_items(db, user_id)

# 수량 변경
async def svc_update_cartItems_quantity(db: AsyncSession, user_id: int, cart_item_id: int, quantity: int):
    """수량 변경 후 전체 장바구니 반환 (cart_item_id 기반)"""
    # 1. CartItem 조회
    item = await rep_get_cartItem_by_id(db, cart_item_id)
    if not item:
        raise ValueError("장바구니 아이템이 존재하지 않습니다.")
    
    cart = await rep_get_cart_by_user_id(db, user_id)
    if not cart or item.cart_id != cart.id:
        raise ValueError("권한이 없습니다.")
    
    if quantity <= 0:
        await db.delete(item)
    else:
        item.quantity = quantity
    
    await db.commit()
    return await svc_get_cart_with_items(db, user_id)

#  아이템 삭제
async def svc_delete_cartItems(db: AsyncSession, user_id: int, cartItem_id: int):
    """아이템 삭제 후 전체 장바구니 반환 (cart_item_id 기반)"""
    item = await rep_get_cartItem_by_id(db, cartItem_id)
    if not item:
        raise ValueError("장바구니 아이템이 존재하지 않습니다.")
    
    cart = await rep_get_cart_by_user_id(db, user_id)
    if not cart or item.cart_id != cart.id:
        raise ValueError("권한이 없습니다.")
    

    await db.delete(item)
    await db.commit()

    return await svc_get_cart_with_items(db, user_id)

# 장바구니 비우기
async def svc_clear_cartItems(db: AsyncSession, user_id: int):
    """장바구니 전체 비운 후 빈 장바구니 반환"""
    cart = await rep_get_cart_by_user_id(db, user_id)
    if not cart:
        raise ValueError("장바구니가 존재하지 않습니다.")
    
    items = await rep_clear_cartItems(db, cart.id)
    await db.commit()
    return await svc_get_cart_with_items(db, user_id)
