from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, BigInteger, ForeignKey, UniqueConstraint, CheckConstraint, func
from typing import List
from datetime import datetime

from models.m_common import Base, TimestampMixin


class Cart(Base, TimestampMixin):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False, unique=True
    )

    # relationships
    user: Mapped["User"] = relationship(back_populates="cart")
    items: Mapped[List["CartItem"]] = relationship(
        back_populates="cart", cascade="all, delete-orphan"
    )


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), index=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # relationships
    cart: Mapped["Cart"] = relationship(back_populates="items")
    product: Mapped["Products"] = relationship()

    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_items_cart_product"),
        CheckConstraint("quantity > 0", name="qty_pos"),
    )
