from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date, Integer, BigInteger, DateTime, ForeignKey, Index
from datetime import date, datetime
from models.m_common import Base


class DailySales(Base):
    """일별 매출 집계 (전체 쇼핑몰)"""
    __tablename__ = "daily_sales"

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    
    # 집계 데이터
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_revenue: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default='now()')

class ProductDailyStats(Base):
    """상품별 일일 통계"""
    __tablename__ = "product_daily_stats"

    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    
    # 집계 데이터
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cart_add_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    purchase_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revenue: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default='now()')
    
    __table_args__ = (
        Index('ix_product_daily_stats_date', 'date'),
        Index('ix_product_daily_stats_product_id', 'product_id'),
    )
