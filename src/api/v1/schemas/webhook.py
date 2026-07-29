from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class WebhookSubscriptionBase(BaseModel):
    url: str = Field(..., description="URL для отправки вебхука")
    events: list[str] = Field(..., min_length=1, description="Список событий, например: ['batch_closed']")
    secret_key: str = Field(..., min_length=8, description="Секрет для подписи запросов (HMAC)")
    is_active: bool = True
    retry_count: int = Field(default=3, ge=0, description="Количество попыток")
    timeout: int = Field(default=10, gt=0, description="Таймаут в секундах")

class WebhookSubscriptionCreate(WebhookSubscriptionBase):
    """Схема для создания подписки (входящие данные от клиента)"""
    pass

class WebhookSubscriptionResponse(WebhookSubscriptionBase):
    """Схема для ответа (исходящие данные из БД)"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)