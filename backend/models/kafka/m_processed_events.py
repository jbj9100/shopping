from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Index, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from models.m_common import Base


class ProcessedEvent(Base):
    """Consumer 멱등성 - 중복 처리 방지"""
    __tablename__ = "processed_events"

    consumer_name: Mapped[str] = mapped_column(String(100), nullable=False, primary_key=True)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default='now()')

    __table_args__ = (
        PrimaryKeyConstraint('consumer_name', 'event_id', name='pk_processed_events'),
        Index('ix_processed_events_processed_at', 'processed_at'),
    )
