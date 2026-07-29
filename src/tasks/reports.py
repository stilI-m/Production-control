import os
import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.celery_app import celery_app
from openpyxl import Workbook

from src.data.models.batch import Batch
from src.storage.minio_service import upload_file_to_minio
from src.core.database import async_session_maker
# создаем асинхронную функцию для вхождения в базу
async def get_batch_data(batch_id: int) -> dict | None:
    """Асинхронно достает данные из базы и сразу конвертирует их в безопасный словарь (DTO)"""
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

@celery_app.task
def generate_batch_report(batch_id: int):
    print(f"Начинаю сборку отчета для партии {batch_id}")

    # 1. Достаем уже безопасный, отвязанный от базы словарь!
    batch_data = asyncio.run(get_batch_data(batch_id))

    if not batch_data:
        print(f"Партия с ID {batch_id} не найдена в базе!")
        return {"status": "error", "message": "Batch not found"}

    # 2. Создаем Excel-книгу
    wb = Workbook()
    ws = wb.active
    # Теперь обращаемся к словарю через квадратные скобки: batch_data['...']
    ws.title = f"Партия {batch_data['batch_number']}"

    # --- ШАПКА ОТЧЕТА ---
    ws.append(["ОТЧЕТ ПО ПРОИЗВОДСТВЕННОЙ ПАРТИИ"])
    ws.append(["Номер партии:", batch_data['batch_number']])
    ws.append(["Номенклатура:", batch_data['nomenclature']])
    ws.append(["Смена:", batch_data['shift']])
    ws.append(["Бригада:", batch_data['team']])
    ws.append(["Станок (ID):", batch_data['work_center_id']])
    ws.append(["Статус:", "Завершена" if batch_data['is_closed'] else "В работе"])
    ws.append([]) # Пустая строка

    # --- ТАБЛИЦА ДЕТАЛЕЙ ---
    ws.append(["Внутренний ID", "Серийный номер (unique_code)", "Статус агрегации", "Дата агрегации"])

    for product in batch_data['products']:
        ws.append([
            product['id'],
            product['unique_code'],
            "Да" if product['is_aggregated'] else "Нет",
            product['aggregated_at']
        ])

    # ... дальше код сохранения файла и отправки в MinIO оставляем без изменений ...
    file_name = f"report_batch_{batch_id}.xlsx"
    temp_file_path = f"/tmp/{file_name}"
    wb.save(temp_file_path)

    uploaded_name = upload_file_to_minio(temp_file_path, file_name, "reports")

    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

    if uploaded_name:
        return {"status": "success", "file": uploaded_name}
    else:
        return {"status": "error", "message": "Failed to upload to MinIO"}