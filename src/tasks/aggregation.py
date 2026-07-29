import asyncio
from sqlalchemy import select, func

from src.core.database import async_session_maker
from src.data.models import Product
from src.celery_app import celery_app
# 1. Асинхронная функция, которая делает реальную работу
async def _aggregate_batch_products_async(batch_id: int):
    # Открываем сессию вручную (без Depends)
    async with async_session_maker() as session:

        query = select(func.count(Product.id)).where(Product.batch_id == batch_id)
        result = await session.execute(query)
        total_products = result.scalar()
        print(f"Агрегация для партии {batch_id} успешно завершена, произведено деталей: {total_products}!")

# 2. Сама Celery-таска (синхронная)
@celery_app.task
def aggregate_batch_products(batch_id: int):
    # Запускаем асинхронный код в синхронной среде
    asyncio.run(_aggregate_batch_products_async(batch_id))
    return True