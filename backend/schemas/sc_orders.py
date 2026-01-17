from typing import List
from datetime import datetime
from .sc_common import APIModel

class OrderItemIn(APIModel):
    product_id: int
    quantity: int


class OrderCreateIn(APIModel):
    items: List[OrderItemIn]
    

class OrderItemOut(APIModel):
    product_id: int
    name: str
    quantity: int
    price: int

class OrderOut(APIModel):
    id: int
    order_number: str
    items_amount: int
    shipping_fee: int
    total_price: int
    created_at: datetime
    items: List[OrderItemOut]

