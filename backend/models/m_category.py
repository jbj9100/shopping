from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, Text
from typing import Optional

from models.m_common import Base, TimestampMixin


class Category(Base, TimestampMixin):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
