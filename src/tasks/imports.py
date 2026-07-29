import asyncio
import logging
from celery import shared_task

# Настраиваем логгер для этой таски вместо print()
logger = logging.getLogger(__name__)

async def _import_batches_async(file_url: str):
    """
    Асинхронное ядро импорта.
    Здесь должна быть логика скачивания файла, вызова utils/excel_parser.py
    и сохранения в базу через BatchService.

    Убрали user_id, так как он не используется.
    """
    logger.info(f"Начинаем обработку файла импорта: {file_url}")

    # Примерный скелет твоей логики:
    # 1. Скачать файл (из MinIO или по URL)
    # 2. parsed_data = parse_excel(file_content)
    # 3. async with async_session_maker() as session:
    #        batch_service = get_batch_service(get_batch_repository(session))
    #        await batch_service.create_batch(...)

    # Эмуляция работы (замени на свой реальный код парсинга)
    await asyncio.sleep(1)

    logger.info(f"Файл {file_url} успешно импортирован.")
    return {"status": "success", "file": file_url}


@shared_task(bind=True, max_retries=3)
def import_batches_task(self, file_url: str):
    """
    Синхронная обертка для Celery.
    Принимает задачу из очереди и запускает асинхронный импорт.
    """
    try:
        # Запускаем асинхронную функцию в синхронном процессе Celery
        result = asyncio.run(_import_batches_async(file_url))
        return result
    except Exception as exc:
        logger.error(f"Сбой при импорте {file_url}: {exc}")
        # Если база отвалилась или файл недоступен - пробуем снова через 60 сек
        raise self.retry(exc=exc, countdown=60)