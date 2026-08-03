from pydantic import BaseModel, Field
from typing import Any

class ImportRequest(BaseModel):
    file_url: str = Field(
        ...,
        description="URL файла (например, в MinIO) для импорта данных",
        examples=["s3://manufacturing-data/imports/batch_123.xlsx"]
    )

class ExportRequest(BaseModel):
    filters: dict | None = Field(
        None,
        description="Словарь с фильтрами для выгрузки (опционально)",
        examples=[{"is_closed": True, "work_center_id": 1}]
    )

class TaskStatusResponse(BaseModel):
    task_id: str = Field(
        ...,
        description="Уникальный UUID задачи в Celery",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    status: str = Field(
        ...,
        description="Текущий статус задачи (PENDING, STARTED, SUCCESS, FAILURE)",
        examples=["SUCCESS"]
    )
    result: Any | None = Field(
        None,
        description="Результат выполнения задачи (например, URL готового отчета или текст ошибки)"
    )