from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.data.models import Base


class WorkCenter(Base):
    __tablename__ = 'work_center'
    id: Mapped[int] = mapped_column(primary_key=True)
    identifier: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default= func.now(),)
    updated_at: Mapped[datetime] = mapped_column(server_default= func.now(),onupdate= func.now())