from typing import List
from .common import APIModel

class CartItemOut(APIModel):
    id: int
    product_id: int
    name: str
    price: int
    quantity: int
    image: str

class CartOut(APIModel):
    items: List[CartItemOut]
    total_price: int
    total_items: int

class CartAddIn(APIModel):
    product_id: int
    quantity: int

class CartUpdateQtyIn(APIModel):
    quantity: int