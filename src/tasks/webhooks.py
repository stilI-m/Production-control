import requests
from celery import shared_task
import logging

logger = logging.getLogger(__name__)
@shared_task(bind=True,
    retry_backoff=True,     # Включает экспоненциальную задержку
    retry_backoff_max=600,  # Максимум 10 минут между попытками
    max_retries=5,
    default_retry_delay=10,
)
def send_webhook_event_task(
        self, 
        target_url: str,
        payload: dict,
        signature: str | None = None
):
    # Используем self.request.id, чтобы в логах было видно, какая именно попытка или задача отрабатывает
    logger.info("Отправка вебхука [Task ID: %s] на URL: %s", self.request.id, target_url)

    headers = {"Content-Type": "application/json"}
    if signature:
        headers["X-Hub-Signature-256"] = f"sha256={signature}"

    try:
        response = requests.post(
            target_url,
            json=payload,
            headers=headers,
            timeout=10
        )
        if response.status_code >= 400:
            logger.warning("Вебхук на %s вернул статус-код %s", target_url, response.status_code)

        response.raise_for_status()
        logger.info("Вебхук успешно доставлен на %s", target_url)
        return {"status": "success", "status_code": response.status_code, "url": target_url}

    except requests.RequestException as exc:
        logger.error("Ошибка сети/сервера при отправке вебхука: %s. Пробуем повторить...", exc)

        raise self.retry(exc=exc)
