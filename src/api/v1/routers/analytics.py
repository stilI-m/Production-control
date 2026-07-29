from fastapi import APIRouter, Depends
from src.core.dependencies import get_analytics_service
from src.domain.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard(
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Получение статистики для главного дашборда. (Данные кэшируются на 5 минут).
    """
    return await analytics_service.get_dashboard_statistics()


@router.get("/batches/{batch_id}/stats")
async def get_batch_stats(
    batch_id: int,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Получение статистики по конкретной партии. (Данные кэшируются на 5 минут).
    """
    return await analytics_service.get_batch_statistics(batch_id)