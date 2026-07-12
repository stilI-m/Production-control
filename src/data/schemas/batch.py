from datetime import datetime, date
from pydantic import BaseModel, ConfigDict

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
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)