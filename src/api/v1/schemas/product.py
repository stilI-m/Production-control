from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    unique_code: str
    batch_id: int
class ProductResponse(BaseModel):
    id: int
    unique_code: str
    batch_id: int
    is_aggregated: bool
    aggregated_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)