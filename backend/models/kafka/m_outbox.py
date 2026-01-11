from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text, BigInteger, DateTime, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional
from datetime import datetime
import uuid

from models.m_common import Base


class OutboxEvent(Base):
    """OutBox Pattern - DB → Kafka 이벤트 발행용"""
    __tablename__ = "outbox_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 이벤트 식별
    aggregate_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'ORDER', 'PRODUCT' 등
    aggregate_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'ORDER_PAID' 등
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Kafka 토픽 라우팅
    topic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Publisher 상태 관리
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='PENDING')
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Publisher 동시성 제어
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default='now()')
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    locked_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default='now()')
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('PENDING','PROCESSING','PUBLISHED','FAILED')", name='chk_outbox_status'),
        # Partial Index는 Alembic 마이그레이션에서 생성
        Index('ix_outbox_aggregate', 'aggregate_type', 'aggregate_id'),
    )
