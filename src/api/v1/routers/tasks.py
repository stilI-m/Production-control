from fastapi import APIRouter, status, Depends
from celery.result import AsyncResult

# Импортируем наш настроенный экземпляр Celery
from src.celery_app import celery_app
from src.core.dependencies import verify_api_key
# Импортируем сами таски
from src.tasks.import_export import import_batches_from_file, export_batches_to_excel
# Импортируем схемы
from src.api.v1.schemas.task import ImportRequest, ExportRequest, TaskStatusResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/import", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(verify_api_key)])
async def start_import_task(data: ImportRequest):
    """
    Запускает фоновую задачу импорта партий.
    Возвращает task_id для отслеживания статуса.
    """
    # Метод .delay() ставит задачу в очередь брокера (RabbitMQ/Redis)
    task = import_batches_from_file.delay(file_url=data.file_url)
    return {"task_id": task.id, "message": "Задача импорта добавлена в очередь"}


@router.post("/export", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(verify_api_key)])
async def start_export_task(data: ExportRequest):
    """
    Запускает фоновую задачу экспорта партий.
    Возвращает task_id для отслеживания статуса.
    """
    task = export_batches_to_excel.delay(filters=data.filters)
    return {"task_id": task.id, "message": "Задача экспорта добавлена в очередь"}


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Проверяет статус выполнения фоновой задачи по её ID.
    """
    task = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task.status,
        "result": None
    }

    if task.state == 'SUCCESS':
        response["result"] = task.result
    elif task.state == 'FAILURE':
        # Подавляем предупреждение тайп-чекера для динамического исключения Celery
        err_msg = str(task.result) if task.result else "Неизвестная ошибка"  # type: ignore
        response["result"] = err_msg
    elif task.state == 'PROGRESS':
        # При PROGRESS достаем наши кастомные метаданные
        response["result"] = task.info

    return response