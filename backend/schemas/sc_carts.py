from typing import List, Optional
from .sc_common import APIModel

class CartItemIn(APIModel):
    product_id: int
    quantity: int

class CartUpdateQtyIn(APIModel):
    quantity: int


class CartItemOut(APIModel):
    """장바구니 아이템 1개 (상품 정보 포함)"""
    id: int                # CartItems.id
    product_id: int        # CartItems.product_id
    product_name: str      # Products.name (join 필요)
    discount_price: int    # 할인 적용된 가격
    product_image: str     # Products.image
    quantity: int          # CartItems.quantity


class CartItemsOut(APIModel):
    """전체 장바구니 조회 응답"""
    items: List[CartItemOut]        # 장바구니 아이템 리스트
    total_items: int                # len(items) (계산)
    total_price: int                # sum(item.subtotal) (계산)

