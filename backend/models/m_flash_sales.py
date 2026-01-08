from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Integer, DateTime, BigInteger, ForeignKey, CheckConstraint, UniqueConstraint, Index, func
)
from sqlalchemy import Enum as SQLEnum
from typing import List
from datetime import datetime
from models.m_common import Base
from enum import Enum


# FlashQueueStatus status 상태용
class FlashQueueStatus(str, Enum):
    WAITING = "WAITING"
    ADMITTED = "ADMITTED"
    EXPIRED = "EXPIRED"
    LEFT = "LEFT"

class FlashSale(Base):
    __tablename__ = "flash_sales"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # relationships
    product: Mapped["Products"] = relationship()
    queue_entries: Mapped[List["FlashSaleQueueEntry"]] = relationship(
        back_populates="flash_sale", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("capacity > 0", name="capacity_pos"),
        CheckConstraint("ends_at > starts_at", name="time_range"),
    )


class FlashSaleQueueEntry(Base):
    __tablename__ = "flash_sale_queue_entries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    flash_sale_id: Mapped[int] = mapped_column(ForeignKey("flash_sales.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status: Mapped[FlashQueueStatus] = mapped_column(SQLEnum(FlashQueueStatus), nullable=False, default=FlashQueueStatus.WAITING)   

    # relationships
    flash_sale: Mapped["FlashSale"] = relationship(back_populates="queue_entries")
    user: Mapped["Users"] = relationship(back_populates="flash_queue_entries")

    __table_args__ = (
        UniqueConstraint("flash_sale_id", "user_id", name="uq_flash_queue_sale_user"),
        CheckConstraint("status IN ('WAITING','ADMITTED','EXPIRED','LEFT')", name="status_allowed"),
        Index("ix_flash_queue_sale_joined", "flash_sale_id", "joined_at"),
    )
