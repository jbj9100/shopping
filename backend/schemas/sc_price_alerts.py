from typing import Optional
from .common import APIModel

class PriceAlertIn(APIModel):
    product_id: int
    target_price: Optional[int] = None

class PriceAlertOut(APIModel):
    id: int
    product_id: int
    target_price: Optional[int] = None
    enabled: bool
