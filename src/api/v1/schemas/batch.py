from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, field_validator


class BatchCreate(BaseModel):
    task_description: str
    shift: str
    team: str
    batch_number: int
    batch_date: date
    nomenclature: str
    ekn_code: str
    shift_start: datetime
    shift_end: datetime
    work_center_id: int
    @field_validator('shift_start', 'shift_end', mode='before')
    @classmethod
    def remove_timezone(cls, v: datetime | str) -> datetime:

        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace('Z', '+00:00'))

        if v.tzinfo is not None:
            v = v.replace(tzinfo=None)
        return v
# Схема для ВОЗВРАТА сменного задания (всё из БД)
class BatchResponse(BaseModel):
    id: int
    is_closed: bool
    closed_at: datetime | None

    task_description: str
    shift: str
    team: str
    batch_number: int
    batch_date: date
    nomenclature: str
    ekn_code: str
    shift_start: datetime
    shift_end: datetime

    work_center_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
class BatchUpdate(BaseModel):
    """
    Схема для частичного обновления партии (PATCH).
    Все поля опциональны, так как мы можем изменить только одно поле (например, is_closed).
    """
    is_closed: bool | None = None
    closed_at: datetime | None = None

    task_description: str | None = None
    shift: str | None = None
    team: str | None = None
    batch_number: int | None = None
    batch_date: date | None = None
    nomenclature: str | None = None
    ekn_code: str | None = None
    shift_start: datetime | None = None
    shift_end: datetime | None = None
    work_center_id: int | None = None

    @field_validator('shift_start', 'shift_end', 'closed_at', mode='before')
    @classmethod
    def remove_timezone(cls, v: datetime | str | None) -> datetime | None:
        """Тот же валидатор, но с поддержкой None"""
        if v is None:
            return v

        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace('Z', '+00:00'))

        if v.tzinfo is not None:
            v = v.replace(tzinfo=None)
        return v