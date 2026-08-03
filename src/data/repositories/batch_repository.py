from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.batch import Batch

from sqlalchemy import func
from src.data.models.product import Product
from sqlalchemy.exc import IntegrityError
from src.core.exceptions import ValidationError

class BatchRepository:
    def __init__(self, session: AsyncSession):
        """Инжектим сессию БД, чтобы не создавать её внутри методов"""
        self.session = session

    async def get_all(self, is_closed: bool | None = None, offset: int = 0, limit: int = 20) -> list[Batch]:
        """Получение списка партий с опциональной фильтрацией"""
        stmt = select(Batch)

        if is_closed is not None:
            stmt = stmt.where(Batch.is_closed == is_closed)

        stmt = stmt.offset(offset).limit(limit).order_by(Batch.id.desc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, batch_id: int) -> Batch | None:
        """Получение одной партии по ID"""
        stmt = select(Batch).where(Batch.id == batch_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_products(self, batch_id: int) -> Batch | None:
        """
        Получение партии вместе с привязанной продукцией.
        Используем selectinload для предотвращения проблемы N+1.
        """
        stmt = (
            select(Batch)
            .options(selectinload(Batch.products))
            .where(Batch.id == batch_id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create(self, data) -> Batch:
        """Создание новой партии. Принимает Pydantic-схему (BatchCreate)"""
        # Преобразуем Pydantic схему в словарь, игнорируя незаданные поля
        new_batch = Batch(**data.model_dump(exclude_unset=True))

        self.session.add(new_batch)
        await self.session.commit()
        await self.session.refresh(new_batch)

        return new_batch

    async def update(self, batch_id: int, data) -> Batch | None:
        """Обновление существующей партии. Принимает Pydantic-схему (BatchUpdate)"""
        stmt = (
            update(Batch)
            .where(Batch.id == batch_id)
            .values(**data.model_dump(exclude_unset=True))
            .returning(Batch)  # Сразу возвращаем обновленную запись
        )
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalar_one_or_none()
        except IntegrityError:
            await self.session.rollback()
            # Бросаем понятную ошибку вместо падения сервера
            raise ValidationError("Нарушение целостности: указан несуществующий work_center_id или product_id")
    async def get_dashboard_stats(self) -> dict:
        total_batches = await self.session.scalar(select(func.count(Batch.id)))
        active_batches = await self.session.scalar(
            select(func.count(Batch.id)).where(Batch.is_closed == False)
        )
        total_products = await self.session.scalar(select(func.count(Product.id)))
        aggregated_products = await self.session.scalar(
            select(func.count(Product.id)).where(Product.is_aggregated == True)
        )

        return {
            "total_batches": total_batches or 0,
            "active_batches": active_batches or 0,
            "total_products": total_products or 0,
            "aggregated_products": aggregated_products or 0,
        }

    async def get_batch_stats(self, batch_id: int) -> dict:
        total_products = await self.session.scalar(
            select(func.count(Product.id)).where(Product.batch_id == batch_id)
        )
        aggregated_products = await self.session.scalar(
            select(func.count(Product.id))
            .where(Product.batch_id == batch_id, Product.is_aggregated == True)
        )
        total = total_products or 0
        aggregated = aggregated_products or 0
        return {
            "total_products": total,
            "aggregated": aggregated,
            "remaining": total - aggregated,
        }