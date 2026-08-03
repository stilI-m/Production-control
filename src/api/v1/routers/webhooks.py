from typing import List
from src.core.exceptions import NotFoundError
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.dependencies import get_webhook_service
from src.domain.services.webhook_service import WebhookService
from src.api.v1.schemas.webhook import WebhookSubscriptionCreate, WebhookSubscriptionResponse
from src.core.dependencies import verify_api_key

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.get("/", response_model=List[WebhookSubscriptionResponse])
async def get_webhooks(
    webhook_service = Depends(get_webhook_service)
):
    """
    Получить список всех активных подписок на вебхуки.
    """
    return await webhook_service.get_all_webhooks()
@router.get("/{webhook_id}", response_model=WebhookSubscriptionResponse)
async def get_webhook(
    webhook_id: int,
    webhook_service = Depends(get_webhook_service)
):
    """
    Получить детали конкретной подписки.
    """
    webhook = await webhook_service.get_webhook_by_id(webhook_id)
    if not webhook:
        raise NotFoundError(f"Вебхук с ID {webhook_id} не найден")
    return webhook

@router.post("", response_model=WebhookSubscriptionResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_api_key)])
async def create_webhook(
    data: WebhookSubscriptionCreate,
    webhook_service: WebhookService = Depends(get_webhook_service),
):
    """Регистрация нового вебхука для получения событий"""
    return await webhook_service.register_webhook(data)


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: int,
    webhook_service: WebhookService = Depends(get_webhook_service),
):
    """Удаление подписки на вебхук"""
    deleted = await webhook_service.remove_webhook(webhook_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка на вебхук не найдена"
        )
