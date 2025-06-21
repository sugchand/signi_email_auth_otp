from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean, Integer
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


def utcnow_timeaware() -> datetime:
    return datetime.now(timezone.utc)


class OTP(Base):
    __tablename__ = "otp"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    otp_code: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow_timeaware
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    attempts_left: Mapped[int] = mapped_column(
        Integer, default=3, nullable=False
    )


class JWT(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow_timeaware
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow_timeaware
    )
