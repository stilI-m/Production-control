from datetime import datetime, timezone
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.product import Product

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def aggregate(self, batch_id: int, code: str) -> Product | None:
        """
        Агрегация продукта. Обновляет статус и время агрегации.
        Использует RETURNING для возврата обновленной строки за один запрос.
        """
        stmt = (
            update(Product)
            .where(
                Product.batch_id == batch_id,
                Product.unique_code == code,
                Product.is_aggregated == False  # Не агрегируем дважды
            )
            .values(
                is_aggregated=True,
                aggregated_at=datetime.now(timezone.utc)
            )
            .returning(Product)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.scalar_one_or_none()