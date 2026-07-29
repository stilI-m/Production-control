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

    async def trigger_event(self, event_type: str, payload: dict) -> None:
        """
        Метод вызывается из других сервисов при наступлении события.
        Находит всех активных подписчиков и отправляет им задачу в Celery.
        """
        subscribers = await self.webhook_repo.get_active_by_event(event_type)

        for sub in subscribers:
            # Если у подписки есть секретный ключ, генерируем HMAC-подпись
            signature = None
            if hasattr(sub, "secret") and sub.secret:
                signature = generate_hmac_signature(payload, sub.secret)

            # Отправляем задачу асинхронной отправки в Celery
            send_webhook_event_task.delay(
                target_url=sub.url,
                payload=payload,
                signature=signature
            )
            pass