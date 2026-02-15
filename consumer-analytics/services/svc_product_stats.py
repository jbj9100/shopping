from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text
from datetime import date, datetime
from models.m_analytics import ProductDailyStats
import logging

logger = logging.getLogger(__name__)


async def update_product_stats(
    db: AsyncSession,
    product_id: int,
    stat_date: date,
    quantity: int,
    amount: int
):
    """
    상품별 일일 통계 업데이트 (UPSERT)
    
    Args:
        db: DB 세션
        product_id: 상품 ID
        stat_date: 통계 날짜
        quantity: 구매 수량
        amount: 매출액 (price * quantity)
    """
    
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    stmt = pg_insert(ProductDailyStats).values(
        product_id=product_id,
        date=stat_date,
        purchase_count=quantity,
        revenue=amount,
        updated_at=datetime.now()
    )
    
    stmt = stmt.on_conflict_do_update(
        index_elements=['product_id', 'date'],
        set_={
            'purchase_count': ProductDailyStats.__table__.c.purchase_count + stmt.excluded.purchase_count,
            'revenue': ProductDailyStats.__table__.c.revenue + stmt.excluded.revenue,
            'updated_at': datetime.now()
        }
    )
    
    await db.execute(stmt)
    logger.info(f"📈 상품 통계 업데이트: product_id={product_id}, +{quantity}개, +{amount}원")


async def get_top_products(db: AsyncSession, target_date: date, limit: int = 10) -> list[dict]:
    """
    특정 날짜의 인기 상품 Top N 조회 (판매량 기준)
    
    Returns:
        [{"product_id": 1, "purchase_count": 50, "revenue": 250000}, ...]
    """
    query = text("""
        SELECT 
            pds.product_id,
            p.name as product_name,
            pds.purchase_count,
            pds.revenue
        FROM product_daily_stats pds
        JOIN products p ON pds.product_id = p.id
        WHERE pds.date = :target_date
        ORDER BY pds.purchase_count DESC
        LIMIT :limit
    """)
    
    result = await db.execute(query, {"target_date": target_date, "limit": limit})
    rows = result.fetchall()
    
    return [
        {
            "product_id": row[0],
            "product_name": row[1],
            "purchase_count": row[2],
            "revenue": row[3]
        }
        for row in rows
    ]
