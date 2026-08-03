from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.api.v1.schemas.batch import BatchResponse, BatchCreate, BatchUpdate
from src.core.dependencies import get_batch_service, verify_api_key
from src.domain.services.batch_service import BatchService
from src.tasks.reports import generate_batch_report
router = APIRouter(prefix="/batches", tags=["Batches"])


@router.get("", response_model=list[BatchResponse])
async def get_batches(
    is_closed: bool | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, gt=0, le=100),
    batch_service: BatchService = Depends(get_batch_service),
):
    """
    Получение списка партий (с поддержкой кэширования в Redis).
    """
    return await batch_service.get_batches_list(
        is_closed=is_closed, offset=offset, limit=limit
    )


@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch_detail(
    batch_id: int,
    batch_service: BatchService = Depends(get_batch_service),
):
    """
    Получение деталей партии с продукцией.
    """
    batch = await batch_service.get_batch_with_products(batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Партия не найдена"
        )
    return batch


@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_api_key)])
async def create_batch(
    data: BatchCreate,
    batch_service: BatchService = Depends(get_batch_service),
):
    """
    Создание новой партии + авто-инвалидация кэша списков и дашборда.
    """
    return await batch_service.create_batch(data)


@router.patch("/{batch_id}", response_model=BatchResponse, dependencies=[Depends(verify_api_key)])
async def update_batch(
    batch_id: int,
    data: BatchUpdate,
    batch_service: BatchService = Depends(get_batch_service),
):
    """
    Обновление партии + авто-инвалидация деталей, статистики и списка.
    """
    batch = await batch_service.update_batch(batch_id, data)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Партия не найдена"
        )
    return batch
@router.post("/{batch_id}/report", status_code=202, dependencies=[Depends(verify_api_key)])
async def request_batch_report(batch_id: int):
    """
    Запускает асинхронную генерацию Excel-отчета по партии.
    Возвращает ID задачи, по которому можно проверить статус.
    """
    task = generate_batch_report.delay(batch_id)
    return {"message": "Генерация отчета запущена", "task_id": task.id}