from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, BigInteger, Text, ForeignKey, CheckConstraint, UniqueConstraint
from typing import List, Optional
from datetime import datetime

from models.m_common import Base, TimestampMixin


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    order_number: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    items_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    shipping_fee: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False)

    shipping_address: Mapped[str] = mapped_column(Text, nullable=False)

    payment_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    payment_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # relationships
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("items_amount >= 0 AND shipping_fee >= 0 AND total_amount >= 0", name="amounts_nonneg"),
        CheckConstraint("total_amount = items_amount + shipping_fee", name="total_eq_sum"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), index=True, nullable=False)

    name_snapshot: Mapped[str] = mapped_column(String(200), nullable=False)
    price_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # relationships
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Products"] = relationship()

    __table_args__ = (
        CheckConstraint("quantity > 0", name="qty_pos"),
        CheckConstraint("price_snapshot >= 0", name="price_nonneg"),
        UniqueConstraint("order_id", "product_id", name="uq_order_items_order_product"),
    )
