from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from datetime import date, datetime
from models.m_analytics import DailySales
import logging

logger = logging.getLogger(__name__)


async def update_daily_sales(db: AsyncSession, order_date: date, order_amount: int):
    """
    일별 매출 통계 업데이트 (UPSERT)
    
    Args:
        db: DB 세션
        order_date: 주문 날짜
        order_amount: 주문 금액
    """
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    
    stmt = pg_insert(DailySales).values(
        date=order_date,
        total_orders=1,
        total_revenue=order_amount,
        updated_at=datetime.now()
    )
    
    # PostgreSQL의 EXCLUDED를 사용하여 UPSERT
    # 충돌 시: 기존 값 + excluded(새 값)
    stmt = stmt.on_conflict_do_update(
        index_elements=['date'],
        set_={
            'total_orders': DailySales.__table__.c.total_orders + stmt.excluded.total_orders,
            'total_revenue': DailySales.__table__.c.total_revenue + stmt.excluded.total_revenue,
            'updated_at': datetime.now()
        }
    )
    
    await db.execute(stmt)
    logger.info(f"📊 일별 매출 업데이트: {order_date}, +{order_amount}원")


async def get_daily_sales(db: AsyncSession, target_date: date) -> dict:
    """
    특정 날짜의 매출 통계 조회
    
    Returns:
        {"date": "2026-01-17", "total_orders": 150, "total_revenue": 7500000}
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(DailySales).where(DailySales.date == target_date)
    )
    row = result.scalar_one_or_none()
    
    if not row:
        return {"date": str(target_date), "total_orders": 0, "total_revenue": 0}
    
    return {
        "date": str(row.date),
        "total_orders": row.total_orders,
        "total_revenue": row.total_revenue
    }
