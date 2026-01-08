from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, BigInteger, Text, Boolean, CheckConstraint, ForeignKey
from typing import Optional
from datetime import datetime

from models.m_common import Base, TimestampMixin


class Products(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    brand: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("categories.id"), nullable=False, index=True)

    price: Mapped[int] = mapped_column(Integer, nullable=False)
    original_price: Mapped[int] = mapped_column(Integer, nullable=False)

    image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    free_shipping: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    depletion_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("price >= 0 AND original_price >= 0", name="price_nonneg"),
        CheckConstraint("price <= original_price", name="price_lte_original"),
        CheckConstraint("stock >= 0", name="stock_nonneg"),
    )