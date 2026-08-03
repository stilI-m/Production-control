from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.data.models import Base


class WorkCenter(Base):
    __tablename__ = 'work_centers'
    id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Внутренний ID станка в базе"
    )
    identifier: Mapped[str] = mapped_column(
        unique=True, index=True,
        comment="Заводской шифр станка (например, 'ЛЕНТА-01')"
    )
    name: Mapped[str] = mapped_column(
        comment="Понятное название (например, 'Конвейер сборки')"
    )
    created_at: Mapped[datetime] = mapped_column(server_default= func.now(),)
    updated_at: Mapped[datetime] = mapped_column(server_default= func.now(),onupdate= func.now())