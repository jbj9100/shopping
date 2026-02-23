from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, Text, Index
from typing import Optional

from models.m_common import Base, TimestampMixin


class Category(Base, TimestampMixin):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index('ix_category_name', 'name'),  # 카테고리명 조회용 (unique=True도 인덱스 생성하지만 명시적 정의)
    )
