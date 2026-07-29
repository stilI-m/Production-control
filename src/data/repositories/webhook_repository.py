from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.webhook import WebhookSubscription


class WebhookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data) -> WebhookSubscription:
        """Создание новой подписки на вебхук"""
        subscription = WebhookSubscription(**data.model_dump(exclude_unset=True))
        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def get_by_id(self, webhook_id: int) -> WebhookSubscription | None:
        """Получение подписки по ID"""
        stmt = select(WebhookSubscription).where(WebhookSubscription.id == webhook_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_event(self, event_type: str) -> list[WebhookSubscription]:
        """Получение всех активных подписчиков, у которых в массиве events есть нужное событие"""
        stmt = select(WebhookSubscription).where(
            WebhookSubscription.is_active.is_(True),
            # Если events это JSONB или ARRAY в PostgreSQL, .contains() найдет вхождение
            WebhookSubscription.events.contains([event_type])
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, webhook_id: int) -> bool:
        """Удаление подписки"""
        stmt = delete(WebhookSubscription).where(WebhookSubscription.id == webhook_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0