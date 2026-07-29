import asyncio
from sqlalchemy import select, func
import logging
from src.core.database import async_session_maker
from src.data.models import Product
from src.celery_app import celery_app
logger = logging.getLogger(__name__)
# 1. Асинхронная функция, которая делает реальную работу
async def _aggregate_batch_products_async(batch_id: int):
    # Открываем сессию вручную (без Depends)
    try:
        async with async_session_maker() as session:
            query = select(func.count(Product.id)).where(Product.batch_id == batch_id)
            result = await session.execute(query)
            total_products = result.scalar()
            logger.info(f"Агрегация для партии %s успешно завершена, произведено деталей: %s", batch_id, total_products)
    except Exception:
        logger.exception("Агрегация для партии %s завершена с ошибкой", batch_id)
        raise
# 2. Сама Celery-таска (синхронная)
@celery_app.task
def aggregate_batch_products(batch_id: int):
    # Запускаем асинхронный код в синхронной среде
    asyncio.run(_aggregate_batch_products_async(batch_id))
    return True