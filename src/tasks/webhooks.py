import httpx
import requests
from celery import shared_task
import logging

logger = logging.getLogger(__name__)
@shared_task(bind=True,
    autoretry_for=(httpx.RequestError, httpx.HTTPStatusError),
    retry_backoff=True,     # Включает экспоненциальную задержку
    retry_backoff_max=600,  # Максимум 10 минут между попытками
    max_retries=5
)
def send_webhook_event_task(
        self,
        target_url: str,
        payload: dict,
        signature: str | None = None
):
    """
    Отправляет HTTP POST запрос на target_url.
    В случае ошибки сети или статуса 4xx/5xx, Celery автоматически сделает retry.
    """
    logger.info("Отправка вебхука на URL: %s", target_url)
    headers = {"Content-Type": "application/json"}
    if signature:
        headers["X-Hub-Signature-256"] = f"sha256={signature}"


    response = requests.post(
        target_url,
        json=payload,
        headers=headers,
        timeout=10
    )
    if response.status_code >= 400:
        logger.warning("Вебхук на %s вернул статус-код %s", target_url, response.status_code)
    # Бросает HTTPError, если сервер вернул ошибку (например, 500)
    # Это исключение тоже является наследником RequestException, поэтому Celery сделает retry.
    response.raise_for_status()
    logger.info("Вебхук успешно доставлен на %s", target_url)
    return {"status": "success", "status_code": response.status_code, "url": target_url}
