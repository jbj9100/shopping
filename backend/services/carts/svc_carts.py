from sqlalchemy.ext.asyncio import AsyncSession
from schemas.sc_carts import CartItemsOut, CartItemOut
from services.products.svc_products import svc_get_products_stock, svc_update_product_stock
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
        # ORM 객체에서 할인가 계산 (10원 단위 반올림)
        calculated_price = product.original_price * (100 - product.discount_percent) / 100
        discount_price = int(round(calculated_price, -1))
        
        cart_items.append(
            CartItemOut(
                id=cart_item.id,
                product_id=cart_item.product_id,
                product_name=product.name,
                product_image=product.image or "",
                discount_price=discount_price,
                quantity=cart_item.quantity,
            )
        )
    
    total_items = len(cart_items)
    total_price = sum(item.discount_price * item.quantity for item in cart_items)
    
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
    
    stock = await svc_get_products_stock(db, product_id)
    if quantity > stock:
        raise ValueError("재고가 부족합니다.")

    if not await svc_update_product_stock(db, product_id, stock - quantity):
        raise ValueError("재고가 부족합니다.")

    existing_item = await rep_get_cartItems_with_product(db, cart.id, product_id)
    
    if existing_item:
        existing_item.quantity += quantity
        await db.commit()
    else:
        await rep_add_cartItems(db, cart.id, product_id, quantity)
        await db.commit()
    
    return await svc_get_cart_with_items(db, user_id)

# 수량 변경
async def svc_update_cartItems_quantity(db: AsyncSession, user_id: int, cartItem_id: int, quantity: int):
    """수량 변경 후 전체 장바구니 반환 (cart_item_id 기반)"""
    # 1. CartItem 조회
    item = await rep_get_cartItem_by_id(db, cartItem_id)
    if not item:
        raise ValueError("장바구니 아이템이 존재하지 않습니다.")
    
    cart = await rep_get_cart_by_user_id(db, user_id)
    if not cart or item.cart_id != cart.id:
        raise ValueError("권한이 없습니다.")
    
    # 장바구니에 담긴 요청수량
    # 10
    old_quantity = item.quantity
    # 재고확인
    # 20
    stock = await svc_get_products_stock(db, item.product_id)
    
    # quantity front에서 계산되서 들어온값이고 0이나 -1로 들어오는 경우는 없지만 혹시 모르는 방어코드
    if quantity <= 0:
        # 요청 수량이 0 이하면 삭제하고 전체 재고 복구
        await svc_update_product_stock(db, item.product_id, stock + old_quantity)
        await db.delete(item)
    else:
        # 요청 수량이 0 이상이면 수량 변경에 따른 재고 조정
        # +1     11            10       수량 증가
        # -1     9             10       수량 감수
        diff = quantity - old_quantity
        if diff > 0:
            # 요청했던 수량보다 더 많은 수량 증가: 재고 차감
            if diff > stock:
                raise ValueError("재고가 부족합니다.")
            await svc_update_product_stock(db, item.product_id, stock - diff)  # 20 - (+1) = 19
        elif diff < 0:
            # 요청했던 수량보다 더 적은 수량 감소: 재고 복구
            await svc_update_product_stock(db, item.product_id, stock - diff)  # 20 - (-1) = 21
        
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
    
    # 삭제 전에 재고 복구
    stock = await svc_get_products_stock(db, item.product_id)
    await svc_update_product_stock(db, item.product_id, stock + item.quantity)

    await db.delete(item)
    await db.commit()

    return await svc_get_cart_with_items(db, user_id)

# 장바구니 비우기
async def svc_clear_cartItems(db: AsyncSession, user_id: int):
    """장바구니 전체 비운 후 빈 장바구니 반환"""
    cart = await rep_get_cart_by_user_id(db, user_id)
    if not cart:
        raise ValueError("장바구니가 존재하지 않습니다.")
    
    # 삭제 전에 모든 아이템의 재고 복구
    items_data = await rep_get_cartItems_with_all_products(db, cart.id)
    for cart_item, product in items_data:
        stock = await svc_get_products_stock(db, cart_item.product_id)
        await svc_update_product_stock(db, cart_item.product_id, stock + cart_item.quantity)

    items = await rep_clear_cartItems(db, cart.id)
    await db.commit()
    return await svc_get_cart_with_items(db, user_id)
