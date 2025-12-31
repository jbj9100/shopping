from typing import List, Optional
from datetime import datetime
from .common import APIModel

class OrderItemIn(APIModel):
    product_id: int
    quantity: int

class OrderCreateIn(APIModel):
    items: List[OrderItemIn]
    shipping_address: str

class OrderItemOut(APIModel):
    product_id: int
    name: str
    quantity: int
    price: int

class OrderOut(APIModel):
    id: int
    order_number: str
    status: str
    items_amount: int
    shipping_fee: int
    total_amount: int
    created_at: datetime
    items: List[OrderItemOut]
