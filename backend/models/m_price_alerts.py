from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, BigInteger, Boolean, ForeignKey, CheckConstraint, UniqueConstraint, func
from typing import Optional
from datetime import datetime

from models.m_common import Base


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)

    target_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # relationships
    user: Mapped["User"] = relationship(back_populates="price_alerts")
    product: Mapped["Products"] = relationship()

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_price_alerts_user_product"),
        CheckConstraint("(target_price IS NULL) OR (target_price >= 0)", name="target_nonneg"),
    )