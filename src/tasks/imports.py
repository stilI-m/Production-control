import os
import asyncio
import logging
from celery import shared_task
from openpyxl import load_workbook

from src.storage.minio_service import s3_client
from src.core.database import async_session_maker
from src.data.repositories.batch_repository import BatchRepository
from src.domain.services.batch_service import BatchService
from src.api.v1.schemas.batch import BatchCreate

logger = logging.getLogger(__name__)

async def _import_batches_async(object_name: str):
    """
    Асинхронное ядро импорта.
    Скачивает файл из MinIO, парсит Excel и сохраняет партии в базу.
    """
    logger.info("Начинаем обработку файла импорта: %s", object_name)
    bucket_name = "imports"

    # Чтобы избежать конфликтов имен при одновременном импорте, можно добавить префикс
    temp_file_path = f"/tmp/import_{object_name.replace('/', '_')}"

    try:
        # 1. Скачиваем файл из MinIO во временную папку
        s3_client.download_file(bucket_name, object_name, temp_file_path)
        logger.info("Файл %s успешно скачан из MinIO во временную директорию", object_name)

        # 2. Парсим Excel файл с помощью openpyxl
        wb = load_workbook(temp_file_path)
        ws = wb.active

        # Предполагаем, что первая строка — это заголовки (batch_number, nomenclature и т.д.)
        headers = [cell.value for cell in ws[1]]

        parsed_batches = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            # Пропускаем пустые строки
            if not any(row):
                continue

            row_data = dict(zip(headers, row))
            parsed_batches.append(row_data)

        logger.info("Извлечено %d строк из файла %s. Начинаем загрузку в БД...", len(parsed_batches), object_name)

        # 3. Сохраняем данные в БД
        imported_count = 0
        async with async_session_maker() as session:
            batch_repo = BatchRepository(session)
            batch_service = BatchService(batch_repo)

            for item in parsed_batches:
                try:
                    # Извлекаем и безопасно конвертируем данные из Excel
                    batch_in = BatchCreate(
                        task_description=str(item.get("task_description", "Импортировано из Excel")),
                        shift=str(item.get("shift", "1")),
                        team=str(item.get("team", "Неизвестно")),
                        # Оборачиваем в int, так как схема требует число
                        batch_number=int(item.get("batch_number", 0)),
                        # Дату и время нужно парсить, если они строковые.
                        # Если openpyxl достает объекты datetime, то оставляем как есть.
                        batch_date=item.get("batch_date"),
                        nomenclature=str(item.get("nomenclature", "N/A")),
                        ekn_code=str(item.get("ekn_code", "N/A")),
                        shift_start=item.get("shift_start"),
                        shift_end=item.get("shift_end"),
                        work_center_id=int(item.get("work_center_id", 0))
                    )

                    # Создаем партию через сервис
                    await batch_service.create_batch(batch_in)
                    imported_count += 1
                except ValueError as ve:
                    logger.warning("Ошибка типов в строке Excel (например, пустая ячейка вместо числа): %s", ve)
                except Exception as e:
                    logger.warning("Ошибка при импорте партии: %s", e)

            # Коммит произойдет внутри create_batch, если у тебя там настроено управление сессией,
            # либо нужно сделать await session.commit() здесь, если create_batch не делает коммит сам.

        logger.info("Успешно импортировано %d/%d партий из файла %s", imported_count, len(parsed_batches), object_name)
        return {"status": "success", "file": object_name, "imported_count": imported_count}

    except Exception as exc:
        logger.exception("Критический сбой при импорте файла %s", object_name)
        raise exc

    finally:
        # 4. Обязательно удаляем временный файл, чтобы не забить диск сервера
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.debug("Временный файл %s удален", temp_file_path)


@shared_task(bind=True, max_retries=3)
def import_batches_task(self, object_name: str):
    """
    Синхронная обертка для Celery.
    Принимает имя объекта (файла) в бакете imports.
    """
    try:
        result = asyncio.run(_import_batches_async(object_name))
        return result
    except Exception as exc:
        logger.exception("Сбой при импорте %s. Повторная попытка...", object_name)
        raise self.retry(exc=exc, countdown=60)