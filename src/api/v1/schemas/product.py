from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ProductCreate(BaseModel):
    unique_code: str = Field(
        ..., min_length=1, max_length=255,
        description="Уникальный код/серийный номер детали",
        examples=["SN-998877"]
    )
    batch_id: int = Field(
        ..., gt=0, le=2147483647,
        description="ID производственной партии",
        examples=[1]
    )

class ProductResponse(BaseModel):
    id: int = Field(..., description="Внутренний ID детали")
    unique_code: str = Field(..., description="Уникальный код/серийный номер детали")
    batch_id: int = Field(..., description="ID производственной партии")
    is_aggregated: bool = Field(..., description="Статус агрегации (привязана ли к партии)")
    aggregated_at: datetime | None = Field(None, description="Время агрегации (в UTC)")
    created_at: datetime = Field(..., description="Время создания записи")

    model_config = ConfigDict(from_attributes=True)