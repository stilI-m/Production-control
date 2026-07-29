import json

from src.data.repositories.webhook_repository import WebhookRepository
from src.utils.hmac_utils import generate_hmac_signature  # Функция подписи полезной нагрузки

from src.tasks.webhooks import send_webhook_event_task


class WebhookService:
    def __init__(self, webhook_repo: WebhookRepository):
        self.webhook_repo = webhook_repo

    async def register_webhook(self, data):
        """Регистрация нового вебхука"""
        return await self.webhook_repo.create(data)

    async def remove_webhook(self, webhook_id: int) -> bool:
        """Удаление вебхука"""
        return await self.webhook_repo.delete(webhook_id)
    async def get_all_webhooks(self):
        return await self.webhook_repo.get_all()

    async def get_webhook_by_id(self, webhook_id: int):
        return await self.webhook_repo.get_by_id(webhook_id)
    async def trigger_event(self, event_type: str, payload: dict) -> None:
        subscribers = await self.webhook_repo.get_active_by_event(event_type)

        # Преобразуем dict в bytes один раз перед циклом
        # sort_keys=True гарантирует одинаковый порядок ключей при сериализации
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')

        for sub in subscribers:
            signature = None
            if hasattr(sub, "secret") and sub.secret:
                # Передаем байты вместо словаря
                signature = generate_hmac_signature(payload_bytes, sub.secret)

            send_webhook_event_task.delay(
                target_url=sub.url,
                payload=payload,
                signature=signature
            )