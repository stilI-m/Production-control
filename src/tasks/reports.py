import os
import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.celery_app import celery_app
from openpyxl import Workbook
import logging
from src.data.models.batch import Batch
from src.storage.minio_service import upload_file_to_minio
from src.core.database import async_session_maker

logger = logging.getLogger(__name__)
# создаем асинхронную функцию для вхождения в базу
async def get_batch_data(batch_id: int) -> dict | None:
    """Асинхронно достает данные из базы и сразу конвертирует их в безопасный словарь (DTO)"""
    try:
        async with async_session_maker() as session:
            query = (
                select(Batch)
                .options(
                    selectinload(Batch.products),
                    selectinload(Batch.work_center)
                )
                .where(Batch.id == batch_id)
            )
            result = await session.execute(query)
            batch = result.scalar_one_or_none()

            if not batch:
                return None

            # МАГИЯ ЗДЕСЬ: "Распаковываем" модель базы данных в простой словарь,
            # пока мы еще внутри async with и сессия жива.
            return {
                "batch_number": batch.batch_number,
                "nomenclature": batch.nomenclature,
                "shift": batch.shift,
                "team": batch.team,
                "work_center_id": batch.work_center.identifier if batch.work_center else "Не указан",
                "is_closed": batch.is_closed,
                "products": [
                    {
                        "id": p.id,
                        "unique_code": p.unique_code,
                        "is_aggregated": p.is_aggregated,
                        "aggregated_at": p.aggregated_at.strftime("%d.%m.%Y %H:%M:%S") if p.aggregated_at else "-"
                    }
                    for p in batch.products
                ]
            }
    except Exception:
        logger.exception("Ошибка при попытке получить данные из базы")
        raise
@celery_app.task
def generate_batch_report(batch_id: int):
    logger.info("Начало сборки отчета для партии %s", batch_id)

    batch_data = asyncio.run(get_batch_data(batch_id))

    if not batch_data:
        logger.error("Партия с ID %s не найдена в базе!", batch_id)
        return {"status": "error", "message": "Batch not found"}

    file_name = f"report_batch_{batch_id}.xlsx"
    temp_file_path = f"/tmp/{file_name}"

    try:
        wb = Workbook()
        ws = wb.active
        ws.title = f"Партия {batch_data['batch_number']}"

        # --- ШАПКА ОТЧЕТА ---
        ws.append(["ОТЧЕТ ПО ПРОИЗВОДСТВЕННОЙ ПАРТИИ"])
        ws.append(["Номер партии:", batch_data['batch_number']])
        ws.append(["Номенклатура:", batch_data['nomenclature']])
        ws.append(["Смена:", batch_data['shift']])
        ws.append(["Бригада:", batch_data['team']])
        ws.append(["Станок (ID):", batch_data['work_center_id']])
        ws.append(["Статус:", "Завершена" if batch_data['is_closed'] else "В работе"])
        ws.append([])

        # --- ТАБЛИЦА ДЕТАЛЕЙ ---
        ws.append(["Внутренний ID", "Серийный номер (unique_code)", "Статус агрегации", "Дата агрегации"])

        for product in batch_data['products']:
            ws.append([
                product['id'],
                product['unique_code'],
                "Да" if product['is_aggregated'] else "Нет",
                product['aggregated_at']
            ])

        wb.save(temp_file_path)

        # Читаем сохраненный Excel-файл как байты
        with open(temp_file_path, "rb") as f:
            file_bytes = f.read()

        # Отправляем байты в MinIO
        uploaded_name = upload_file_to_minio(file_bytes, file_name, "reports")

        if uploaded_name:
            logger.info("Успешная загрузка файла %s в MinIO", file_name)
            return {"status": "success", "file": uploaded_name}
        else:
            logger.error("Не удалось загрузить файл %s в MinIO", file_name)
            return {"status": "error", "message": "Failed to upload to MinIO"}

    except Exception:
        logger.exception("Ошибка в процессе генерации отчета для партии %s", batch_id)
        raise
    finally:
        # Гарантированно удаляем файл из /tmp при любом исходе (успех или ошибка)
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)