from datetime import datetime, date

from sqlalchemy import ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data.models import Base


class Batch(Base):
    __tablename__ = 'batches'
    id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Внутренний ID партии (технический)"
    )
    is_closed: Mapped[bool] = mapped_column(
        default=False,
        comment="Статус задания: False - в работе, True - завершено"
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        default=None,
        comment="Точное время, когда партию завершили"
    )
    task_description: Mapped[str] = mapped_column(
        comment="Текстовое описание: что именно нужно сделать"
    )
    shift: Mapped[str] = mapped_column(
        comment="Название или номер смены (например, 'Ночная' или 'Смена 1')"
    )
    team: Mapped[str] = mapped_column(
        comment="Кто выполняет работу (например, 'Бригада 1')"
    )
    batch_number: Mapped[int] = mapped_column(
        index=True,
        comment="Производственный номер партии (как в 1С или на бумаге)"
    )
    batch_date: Mapped[date] = mapped_column(
        index=True,
        comment="Дата производства партии"
    )
    nomenclature: Mapped[str] = mapped_column(
        comment="Что производим (например, 'Гайка М12')"
    )
    ekn_code: Mapped[str] = mapped_column(
        comment="Артикул / Внутренний код номенклатуры завода"
    )
    shift_start: Mapped[datetime] = mapped_column(
        comment="Во сколько смена началась"
    )
    shift_end: Mapped[datetime] = mapped_column(
        comment="Во сколько смена должна закончиться"
    )

    # ВНЕШНИЕ КЛЮЧИ И СВЯЗИ
    work_center_id: Mapped[int] = mapped_column(
        ForeignKey('work_centers.id'),
        comment="Ссылка на станок: на каком оборудовании это делается"
    )

    # Связи (relationships) не создают колонок в базе, они нужны только для Алхимии (чтобы удобно писать product.batch)
    products: Mapped[list["Product"]] = relationship(back_populates="batch")
    work_center: Mapped["WorkCenter"] = relationship()
    __table_args__ = (
        UniqueConstraint('batch_number', 'batch_date', name='uq_batch_number_date'),
        Index('idx_batch_closed', 'is_closed'),
        Index('idx_batch_shift_times', 'shift_start', 'shift_end'),
    )