from typing import Optional, List
from datetime import datetime
from .sc_common import APIModel


class ProductFilter(APIModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_discount: Optional[int] = None
    max_discount: Optional[int] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    min_review_count: Optional[int] = None
    max_review_count: Optional[int] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None
    min_depletion_eta_minutes: Optional[int] = None
    max_depletion_eta_minutes: Optional[int] = None

class ProductFilterOut(ProductFilter):
    total_count: int

class ProductIn(APIModel):
    name: str
    price: int
    original_price: int
    brand: str
    category_id: int
    image: str
    free_shipping: bool
    stock: int
    description: Optional[str] = None
    depletion_eta_minutes: Optional[int] = None


class ProductOut(APIModel):
    id: int
    name: str
    price: int
    original_price: int
    brand: str
    category_id: int  
    image: str
    free_shipping: bool
    stock: int
    description: Optional[str] = None
    depletion_eta_minutes: Optional[int] = None
