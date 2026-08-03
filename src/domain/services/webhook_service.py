import json

from src.data.repositories.webhook_repository import WebhookRepository
from src.utils.hmac_utils import generate_hmac_signature  # Функция подписи полезной нагрузки

from src.tasks.webhooks import send_webhook_event_task
import logging
logger = logging.getLogger(__name__)
class WebhookService:
    def __init__(self, webhook_repo: WebhookRepository):
        self.webhook_repo = webhook_repo

    async def register_webhook(self, data):
        """Регистрация нового вебхука"""
        try:
            registration = await self.webhook_repo.create(data)
            if registration:
                logger.info("Успешно зарегистрирован вебхук ID: %s на URL: %s", registration.id, registration.url)
            return registration
        except Exception as e:
            logger.exception("Ошибка при регистрации вебхука с URL: %s", data.url)
            raise e

    async def remove_webhook(self, webhook_id: int) -> bool:
        """Удаление вебхука"""
        try:
            removing = await self.webhook_repo.delete(webhook_id)
            if removing:
                logger.info("Успешно удален вебхук ID: %s", webhook_id)
            return removing
        except Exception as e:
            logger.exception("Ошибка при удалении вебхука с id: %s", webhook_id)
            raise e
    async def get_all_webhooks(self):
        """Получение всех вебхуков"""
        try:
            get_all_webhooks = await self.webhook_repo.get_all()
            if get_all_webhooks:
                logger.info("Успешно получены все вебхуки")
            return get_all_webhooks
        except Exception as e:
            logger.exception("Ошибка при получении всех вебхуков")
            raise e
    async def get_webhook_by_id(self, webhook_id: int):
        """Получение вебхука по ID"""
        try:
            getting = await self.webhook_repo.get_by_id(webhook_id)
            if getting:
                logger.info("Успешно получен вебхук ID: %s", webhook_id)
            return getting
        except Exception as e:
            logger.exception("Ошибка при получении вебхука с id: %s", webhook_id)
            raise e
    async def trigger_event(self, event_type: str, payload: dict) -> None:
        """Инициация отправки вебхуков всем подписчикам события"""
        try:
            subscribers = await self.webhook_repo.get_active_by_event(event_type)

            # Если подписчиков нет, это не ошибка, но это полезно знать
            if not subscribers:
                logger.info("Нет активных подписчиков для события: %s", event_type)
                return

            # Логируем, сколько человек получат уведомление
            logger.info(
                "Событие %s: найдено %d подписчиков. Формируем задачи для Celery...",
                event_type,
                len(subscribers)
            )

            # Преобразуем dict в bytes один раз перед циклом
            payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')

            for sub in subscribers:
                signature = None
                if hasattr(sub, "secret_key") and sub.secret_key:
                    signature = generate_hmac_signature(payload_bytes, sub.secret_key)

                # Отправляем задачу в очередь Celery
                send_webhook_event_task.delay(
                    target_url=sub.url,
                    payload=payload,
                    signature=signature
                )

            logger.info("Задачи по вебхукам для события %s успешно переданы в очередь", event_type)

        except Exception as e:
            logger.exception("Ошибка при генерации вебхуков для события: %s", event_type)
            raise e