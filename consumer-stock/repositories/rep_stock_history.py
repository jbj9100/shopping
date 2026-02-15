from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.m_stock_history import StockHistory
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)


async def create_stock_history_idempotent(
    db: AsyncSession,
    event_id: uuid.UUID,
    product_id: int,
    order_id: Optional[int],
    reason: str,
    stock_before: int,
    stock_after: int,
    delta: int
) -> Optional[StockHistory]:
    """
    event_id 기반 멱등성 보장
    - 이미 존재하면 None 반환 (중복 처리 방지)
    - 새로 생성하면 StockHistory 객체 반환
    """
    # 1. 중복 체크 (Unique Index 활용)
    stmt = select(StockHistory).where(StockHistory.event_id == event_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        logger.debug(f"⏭️ 중복 이벤트, 이미 처리됨: event_id={event_id}")
        return None  # 이미 처리됨
    
    # 2. 새로 생성
    history = StockHistory(
        event_id=event_id,
        product_id=product_id,
        order_id=order_id,
        reason=reason,
        stock_before=stock_before,
        stock_after=stock_after,
        delta=delta
    )
    db.add(history)
    return history
