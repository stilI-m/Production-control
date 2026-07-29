import requests
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def send_webhook_event_task(
        self,
        target_url: str,
        payload: dict,
        signature: str | None = None
):
    """
    Отправляет HTTP POST запрос на target_url.
    В случае неудачи делает 3 попытки с увеличивающейся задержкой.
    """
    headers = {"Content-Type": "application/json"}

    # Если есть HMAC подпись, добавляем её в заголовки
    if signature:
        headers["X-Hub-Signature-256"] = f"sha256={signature}"

    try:
        # Устанавливаем timeout, чтобы таска не зависла навечно, если чужой сервер "тупит"
        response = requests.post(
            target_url,
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status() # Бросит исключение, если статус 4xx или 5xx

        # Здесь в будущем можно добавить логирование в WebhookDelivery
        return {"status": "success", "status_code": response.status_code, "url": target_url}

    except requests.exceptions.RequestException as exc:
        # Ловим любые ошибки сети и переотправляем таску
        # countdown = 2 ** self.request.retries даст задержки: 1 сек, 2 сек, 4 сек...
        print(f"Ошибка отправки вебхука на {target_url}: {exc}. Пробуем еще раз...")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)