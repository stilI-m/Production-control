from pydantic import BaseModel
from typing import Any

class ImportRequest(BaseModel):
    file_url: str

class ExportRequest(BaseModel):
    filters: dict | None = None

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Any | None = None