from typing import Optional, List
from datetime import datetime
from .sc_common import APIModel


class ProductOut(APIModel):
    id: int
    name: str
    price: int
    original_price: int
    discount: int
    brand: str
    image: str
    rating: float
    review_count: int
    free_shipping: bool
    stock: int
    depletion_eta_minutes: Optional[int] = None

class ProductDetailOut(ProductOut):
    description: Optional[str] = None