from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field, field_validator


class BatchCreate(BaseModel):
    task_description: str = Field(
        ..., min_length=1, max_length=255, description="Описание задачи", examples=["Производство партий А"]
    )
    shift: str = Field(..., min_length=1, max_length=50, description="Смена", examples=["1"])
    team: str = Field(..., min_length=1, max_length=50, description="Бригада", examples=["Бригада №2"])
    batch_number: int = Field(
        ..., gt=0, le=2147483647, description="Номер партии (от 1 до 2 147 483 647)", examples=[101]
    )
    batch_date: date = Field(..., description="Дата смены", examples=["2026-07-29"])
    nomenclature: str = Field(
        ..., min_length=1, max_length=100, description="Номенклатура", examples=["Втулка N-909"]
    )
    ekn_code: str = Field(..., min_length=1, max_length=50, description="Код ЕКН", examples=["ERN-123"])
    shift_start: datetime = Field(..., description="Время начала смены")
    shift_end: datetime = Field(..., description="Время окончания смены")
    work_center_id: int = Field(
        ..., gt=0, le=2147483647, description="ID рабочего центра (должен существовать в БД)", examples=[1]
    )

    @field_validator('shift_start', 'shift_end', mode='before')
    @classmethod
    def remove_timezone(cls, v: datetime | str) -> datetime:
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace('Z', '+00:00'))
        if isinstance(v, datetime) and v.tzinfo is not None:
            v = v.replace(tzinfo=None)
        return v


class BatchUpdate(BaseModel):
    """Схема для частичного обновления партии (PATCH)."""
    is_closed: bool | None = Field(None, description="Статус закрытия партии")
    closed_at: datetime | None = Field(None, description="Время закрытия партии")

    task_description: str | None = Field(None, min_length=1, max_length=255, description="Описание задачи")
    shift: str | None = Field(None, min_length=1, max_length=50, description="Смена")
    team: str | None = Field(None, min_length=1, max_length=50, description="Бригада")
    batch_number: int | None = Field(None, gt=0, le=2147483647, description="Номер партии")
    batch_date: date | None = Field(None, description="Дата смены")
    nomenclature: str | None = Field(None, min_length=1, max_length=100, description="Номенклатура")
    ekn_code: str | None = Field(None, min_length=1, max_length=50, description="Код ЕКН")
    shift_start: datetime | None = Field(None, description="Время начала смены")
    shift_end: datetime | None = Field(None, description="Время окончания смены")
    work_center_id: int | None = Field(None, gt=0, le=2147483647, description="ID рабочего центра")

    @field_validator('shift_start', 'shift_end', 'closed_at', mode='before')
    @classmethod
    def remove_timezone(cls, v: datetime | str | None) -> datetime | None:
        if v is None:
            return v
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace('Z', '+00:00'))
        if isinstance(v, datetime) and v.tzinfo is not None:
            v = v.replace(tzinfo=None)
        return v


class BatchResponse(BaseModel):
    id: int
    is_closed: bool
    closed_at: datetime | None = None

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