# models/__init__.py 
# 일반 디렉터리였던 models를 패키지로 지정해서 import할때 편하게 할 수 있다
# 
# ❌ 긴 경로
# from models.m_user import User
# from models.m_carts import Cart
# from models.m_orders import Order
# ✅ 짧고 명확
# from models import *    __all__에 있는거 다 import


from models.m_common import Base, TimestampMixin
from models.m_user import Users, UserSession
from models.m_carts import Carts, CartItems
from models.m_products import Products
from models.m_orders import Orders, OrderItems
from models.m_price_alerts import PriceAlert
from models.m_flash_sales import FlashSale, FlashSaleQueueEntry

__all__ = [
    "Base",
    "TimestampMixin",
    "Users",
    "UserSession",
    "Carts",
    "CartItems",
    "Products",
    "Orders",
    "OrderItems",
    "PriceAlert",
    "FlashSale",
    "FlashSaleQueueEntry",
]
