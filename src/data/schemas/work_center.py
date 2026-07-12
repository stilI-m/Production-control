from datetime import datetime
from pydantic import BaseModel, ConfigDict


# Схема для СОЗДАНИЯ (только то, что вводит пользователь)
class WorkCenterCreate(BaseModel):
    identifier: str
    name: str

# Схема для ВОЗВРАТА (все поля базы + настройка для чтения ORM-объектов)
class WorkCenterResponse(BaseModel):
    id: int
    identifier: str
    name: str
    created_at: datetime
    updated_at: datetime
    # Разрешаем Pydantic парсить объекты SQLAlchemy
    model_config = ConfigDict(from_attributes=True)