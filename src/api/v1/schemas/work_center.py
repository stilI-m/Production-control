from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class WorkCenterCreate(BaseModel):
    identifier: str = Field(
        ..., min_length=1, max_length=50,
        description="Уникальный строковый идентификатор рабочего центра",
        examples=["WC-Line-01"]
    )
    name: str = Field(
        ..., min_length=1, max_length=150,
        description="Полное название рабочего центра",
        examples=["Сборочная линия №1"]
    )

class WorkCenterResponse(BaseModel):
    id: int = Field(..., description="ID рабочего центра в БД")
    identifier: str = Field(..., description="Уникальный строковый идентификатор")
    name: str = Field(..., description="Полное название рабочего центра")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(..., description="Время последнего обновления")

    model_config = ConfigDict(from_attributes=True)