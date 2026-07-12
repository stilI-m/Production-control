from datetime import datetime, date

from sqlalchemy import func, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data.models import Base


class Batch(Base):
    __tablename__ = 'batches'
    id: Mapped[int] = mapped_column(primary_key=True)
    is_closed: Mapped[bool] = mapped_column(default=False)
    closed_at: Mapped[datetime | None] = mapped_column(default=None)
    task_description: Mapped[str] = mapped_column()
    shift: Mapped[str] = mapped_column()
    team: Mapped[str] = mapped_column()
    batch_number: Mapped[int] = mapped_column(index=True)
    batch_date: Mapped[date] = mapped_column(index=True)
    nomenclature: Mapped[str] = mapped_column()
    ekn_code: Mapped[str] = mapped_column()
    shift_start: Mapped[datetime] = mapped_column()
    shift_end: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    products: Mapped[list["Product"]] = relationship(back_populates="batch")
    work_center: Mapped["WorkCenter"] = relationship()
    work_center_id: Mapped[int] = mapped_column(ForeignKey('work_centers.id'))
    __table_args__ = (
        UniqueConstraint('batch_number', 'batch_date', name='uq_batch_number_date'),
        Index('idx_batch_closed', 'is_closed'),
        Index('idx_batch_shift_times', 'shift_start', 'shift_end'),
    )