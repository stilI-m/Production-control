from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_maker

from src.domain.services.batch_service import BatchService

from src.data.repositories.product_repository import ProductRepository
from src.domain.services.product_service import ProductService

from src.data.repositories.batch_repository import BatchRepository
from src.domain.services.analytics_service import AnalyticsService

from src.data.repositories.webhook_repository import WebhookRepository
from src.domain.services.webhook_service import WebhookService

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Генератор асинхронных сессий базы данных.
    Автоматически закрывает сессию после завершения HTTP-запроса.
    """
    async with async_session_maker() as session:
        yield session


def get_batch_repository(
    session: AsyncSession = Depends(get_db)
) -> BatchRepository:
    """Инжектим сессию БД в репозиторий партий"""
    return BatchRepository(session)


def get_batch_service(
    batch_repo: BatchRepository = Depends(get_batch_repository)
) -> BatchService:
    """Инжектим репозиторий в сервис партий"""
    return BatchService(batch_repo)

def get_product_repository(
    session: AsyncSession = Depends(get_db)
) -> ProductRepository:
    """Инжектим сессию в репозиторий продуктов"""
    return ProductRepository(session)

def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository)
) -> ProductService:
    """Инжектим репозиторий в сервис продуктов"""
    return ProductService(product_repo)

def get_analytics_service(
    batch_repo: BatchRepository = Depends(get_batch_repository)
) -> AnalyticsService:
    return AnalyticsService(batch_repo)

def get_webhook_repository(
    session: AsyncSession = Depends(get_db)
) -> WebhookRepository:
    return WebhookRepository(session)


def get_webhook_service(
    webhook_repo: WebhookRepository = Depends(get_webhook_repository)
) -> WebhookService:
    return WebhookService(webhook_repo)