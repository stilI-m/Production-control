import os
import asyncio
import logging
import openpyxl
from datetime import datetime
from sqlalchemy import select, insert
from openpyxl import Workbook

from src.celery_app import celery_app
from src.core.database import async_session_maker
from src.storage.minio_service import download_file_from_minio, upload_file_to_minio
from src.data.models.batch import Batch
from src.core.cache import CacheService

# Настраиваем логгер
logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=1)
def import_batches_from_file(self, file_url: str):  # <-- Убрали user_id
    """
    Асинхронная задача Celery для импорта партий из Excel/CSV файла.
    """
    return asyncio.run(_import_batches_async(self, file_url))


async def _import_batches_async(task, file_url: str):
    temp_path = f"/tmp/import_{task.request.id}.xlsx"
    logger.info(f"Начинаем скачивание файла из MinIO: {file_url}")

    # 1. Скачиваем файл из MinIO
    try:
        download_file_from_minio(file_url, temp_path, bucket_name="imports")
    except Exception as e:
        logger.error(f"Ошибка скачивания: {e}")
        return {
            "success": False,
            "total_rows": 0, "created": 0, "skipped": 0,
            "errors": [{"row": 0, "error": f"Не удалось скачать файл из MinIO: {str(e)}"}]
        }

    # 2. Открываем Excel
    wb = openpyxl.load_workbook(temp_path, read_only=True)
    ws = wb.active
    total_rows = max(0, ws.max_row - 1)
    created, skipped = 0, 0
    errors, valid_rows_data = [], []

    # 3. Открываем сессию (в Celery зависимость Depends не работает, так что юзаем session_maker напрямую)
    async with async_session_maker() as session:
        for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                # Защита от пустых строк
                if not row or row[0] is None or str(row[0]).strip() == "":
                    continue

                if total_rows > 0 and (i - 1) % 10 == 0:
                    task.update_state(
                        state='PROGRESS',
                        meta={'current': i - 1, 'total': total_rows, 'created': created, 'skipped': skipped}
                    )

                raw_batch_number = row[0]
                batch_date = row[1]
                nomenclature = row[2] if len(row) > 2 else None
                task_description = row[3] if len(row) > 3 else None
                shift = row[4] if len(row) > 4 else None
                team = row[5] if len(row) > 5 else None
                ekn_code = row[6] if len(row) > 6 else None
                shift_start = row[7] if len(row) > 7 else None
                shift_end = row[8] if len(row) > 8 else None
                work_center_id = row[9] if len(row) > 9 else None

                if not batch_date or not ekn_code or not task_description or not shift_start or not shift_end or not work_center_id:
                    raise ValueError("Заполнены не все обязательные поля")

                batch_number = int(raw_batch_number)
                parsed_work_center_id = int(work_center_id)

                def parse_dt(val):
                    if isinstance(val, str):
                        return datetime.strptime(val.strip(), "%Y-%m-%d %H:%M:%S")
                    return val

                parsed_batch_date = batch_date.date() if isinstance(batch_date, datetime) else datetime.strptime(str(batch_date), "%Y-%m-%d").date()
                parsed_shift_start = parse_dt(shift_start)
                parsed_shift_end = parse_dt(shift_end)

                # Проверка на дубликаты
                stmt = select(Batch).where(
                    Batch.batch_number == batch_number,
                    Batch.batch_date == parsed_batch_date
                )
                result = await session.execute(stmt)
                if result.scalar_one_or_none():
                    skipped += 1
                    errors.append({"row": i, "error": "Duplicate batch number and date"})
                    continue

                valid_rows_data.append({
                    "batch_number": batch_number,
                    "batch_date": parsed_batch_date,
                    "nomenclature": str(nomenclature) if nomenclature else None,
                    "task_description": str(task_description),
                    "shift": str(shift) if shift else None,
                    "team": str(team) if team else None,
                    "ekn_code": str(ekn_code),
                    "shift_start": parsed_shift_start,
                    "shift_end": parsed_shift_end,
                    "work_center_id": parsed_work_center_id
                })
                created += 1

            except Exception as e:
                skipped += 1
                errors.append({"row": i, "error": str(e)})

        # 4. Массовая вставка в БД
        if valid_rows_data:
            try:
                await session.execute(insert(Batch), valid_rows_data)
                await session.commit()

                # 🔥 ВАЖНО: Сбрасываем кэш, так как данные в базе изменились!
                logger.info("Массовая вставка успешна. Очищаем кэш дашборда и списков.")
                await CacheService.delete("dashboard_stats")
                await CacheService.delete_pattern("batches_list:*")

            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка массовой вставки: {e}")
                return {"success": False, "error": f"Ошибка вставки: {str(e)}"}

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return {"success": True, "total_rows": total_rows, "created": created, "skipped": skipped, "errors": errors}


@celery_app.task(bind=True)
def export_batches_to_excel(self, filters: dict = None):
    """Фоновая задача для экспорта партий в Excel."""
    return asyncio.run(_export_batches_async(self, filters))


async def _export_batches_async(task, filters: dict):
    if filters is None:
        filters = {}

    async with async_session_maker() as session:
        stmt = select(Batch)
        result = await session.execute(stmt)
        batches = result.scalars().all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Отчет по партиями"

    headers = [
        "ID", "Номер партии", "Дата партии", "Номенклатура",
        "Описание", "Смена", "Бригада", "Код ЕКН",
        "Начало смены", "Конец смены", "Закрыта"
    ]
    ws.append(headers)

    for b in batches:
        ws.append([
            b.id,
            b.batch_number,
            b.batch_date.strftime("%Y-%m-%d") if b.batch_date else "",
            b.nomenclature,
            b.task_description,
            b.shift,
            b.team,
            b.ekn_code,
            b.shift_start.strftime("%Y-%m-%d %H:%M:%S") if b.shift_start else "",
            b.shift_end.strftime("%Y-%m-%d %H:%M:%S") if b.shift_end else "",
            "Да" if b.is_closed else "Нет"
        ])

    file_name = f"export_{task.request.id}.xlsx"
    temp_path = f"/tmp/{file_name}"
    wb.save(temp_path)

    try:
        with open(temp_path, "rb") as f:
            file_bytes = f.read()
        upload_file_to_minio(file_bytes=file_bytes, object_name=file_name, bucket_name="exports")
    except Exception as e:
        logger.error(f"Ошибка выгрузки в MinIO: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return {"success": False, "error": f"Ошибка загрузки в MinIO: {str(e)}"}

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return {
        "success": True,
        "total_exported": len(batches),
        "file_name": file_name,
        "bucket": "exports",
        "message": "Экспорт успешно завершен"
    }