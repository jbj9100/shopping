from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Index

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    created_dt: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # cookie의 value값
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)  # users테이블의 id를 참조
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)  
    # 로그인 유지 기간으로 이 시간 이후엔 무조건 세션 무효
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # expires_at와 상관없이 이 값이 있으면 즉시 무효, 나중에 감사/추적할때 사용할 컬럼

    user: Mapped["User"] = relationship("User") # ORM의 편의기능으로 User 객체를 바로 접근 가능

    __table_args__ = (  # DB가 더 빨리 찾게 인덱스를 만들어두는 것
        Index("ix_user_sessions_valid", "user_id", "expires_at", "revoked_at"),
    )