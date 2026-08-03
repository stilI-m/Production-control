from datetime import datetime

from sqlalchemy import func, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data.models import Base


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Внутренний ID детали"
    )
    unique_code: Mapped[str] = mapped_column(
        unique=True, index=True,
        comment="Тот самый СЕРИЙНЫЙ НОМЕР (уникальный штрихкод, RFID, QR-код детали)"
    )
    batch_id: Mapped[int] = mapped_column(
        ForeignKey("batches.id"), index=True,
        comment="Ссылка на сменное задание: в рамках какой партии создана эта деталь"
    )
    is_aggregated: Mapped[bool] = mapped_column(
        default=False, index=True,
        comment="Участвовала ли эта деталь в массовой агрегации (наша Celery-таска)"
    )
    aggregated_at: Mapped[datetime | None] = mapped_column(
        default=None,
        comment="Когда именно деталь была сагрегирована"
    )

    # Связь с таблицей Batches (чтобы легко получить партию из детали)
    batch: Mapped['Batch'] = relationship(back_populates="products")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    __table_args__ = (
        Index('idx_product_batch_aggregated', 'batch_id', 'is_aggregated'),
    )
