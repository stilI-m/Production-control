from datetime import datetime
from pydantic import ConfigDict
from pydantic import BaseModel, Field, HttpUrl, field_validator
from urllib.parse import urlparse
class WebhookSubscriptionBase(BaseModel):
    url: HttpUrl = Field(..., description="URL для отправки вебхука")
    @field_validator("url")
    def validate_url_is_https(cls, v):
        # v - это объект Url в Pydantic v2
        url_str = str(v)
        parsed = urlparse(url_str)

        if parsed.scheme != "https":
            raise ValueError("URL вебхука должен использовать только HTTPS протокол")

        # Базовая защита от обращений к локалхосту
        if parsed.hostname in ["localhost", "127.0.0.1", "0.0.0.0"]:
            raise ValueError("Использование локальных адресов запрещено")

        return v
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
    secret_key: str | None = Field(default=None, exclude=True)
    model_config = ConfigDict(from_attributes=True)