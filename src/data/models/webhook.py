from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, JSON, Integer, DateTime, ARRAY, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data.models import Base


class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String, nullable=False)

    events: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    secret_key: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=3)
    timeout: Mapped[int] = mapped_column(Integer, default=10)

    # Даты (используем func.now() для автоматической простановки на уровне БД)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Обратная связь для SQLAlchemy
    deliveries: Mapped[list["WebhookDelivery"]] = relationship(
        back_populates="subscription",
        cascade="all, delete-orphan"
    )


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("webhook_subscriptions.id", ondelete="CASCADE")
    )
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    response_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)

    # Даты по ТЗ
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Связь с подпиской
    subscription: Mapped["WebhookSubscription"] = relationship(back_populates="deliveries")