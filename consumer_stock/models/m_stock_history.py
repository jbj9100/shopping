from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, BigInteger, DateTime, CheckConstraint, Index, text
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional
from datetime import datetime
import uuid

from models.m_common import Base


class StockHistory(Base):
    """재고 변동 이력 - 감사 로그"""
    __tablename__ = "stock_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # 연관 엔티티 (ForeignKey 제거 - Consumer는 참조 불필요)
    product_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    order_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # 이벤트 추적
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    reason: Mapped[str] = mapped_column(String(50), nullable=False)  # 'ORDER_PAID', 'ORDER_CANCELED', 'RESTOCKED'

    # 재고 스냅샷
    stock_before: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_after: Mapped[int] = mapped_column(Integer, nullable=False)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)  # +10 or -5

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default='now()')

    __table_args__ = (
        CheckConstraint('stock_after = stock_before + delta', name='chk_stock_delta'),
        Index('ix_stock_history_product_id', 'product_id'),  # 상품별 이력 조회용
        Index('ix_stock_history_product_created', 'product_id', 'created_at'),
        Index('ix_stock_history_order', 'order_id'),
        # Consumer 멱등성: 같은 이벤트로 중복 이력 생성 방지 (event_id가 NULL이 아닌 경우만 UNIQUE)
        Index(
            'ix_stock_history_event_idempotency',
            'event_id',
            unique=True,
            postgresql_where=text("event_id IS NOT NULL")  # Partial Unique Index
        ),
    )
