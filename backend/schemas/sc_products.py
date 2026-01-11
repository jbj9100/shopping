from typing import Optional, List
from datetime import datetime
from pydantic import computed_field
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
    original_price: int
    discount_percent: int = 0
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
    original_price: int
    discount_percent: int = 0
    brand: str
    category_id: int  
    image: str
    view_count: int
    free_shipping: bool
    stock: int
    description: Optional[str] = None
    depletion_eta_minutes: Optional[int] = None
    
    @computed_field # model_dump같은 역할 , pydantic객체를 dict로 변환할 때 사용
    @property  # price를 메서드처럼 호출하지 않고 obj.price로 접근하게 해줌
    def price(self) -> int:
        """할인율을 적용한 판매가 계산 (10원 단위 반올림)"""
        calculated_price = self.original_price * (100 - self.discount_percent) / 100
        return int(round(calculated_price, -1))  # 10원 단위 반올림
