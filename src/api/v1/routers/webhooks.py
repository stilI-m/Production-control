from fastapi import APIRouter, Depends, HTTPException, status

from src.core.dependencies import get_webhook_service
from src.domain.services.webhook_service import WebhookService
from src.api.v1.schemas.webhook import WebhookSubscriptionCreate, WebhookSubscriptionResponse

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("", response_model=WebhookSubscriptionResponse, status_code=status.HTTP_201_CREATED)
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