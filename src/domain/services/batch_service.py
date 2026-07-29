from src.core.cache import cached, CacheService
from src.data.repositories.batch_repository import BatchRepository
from src.api.v1.schemas.batch import BatchCreate, BatchUpdate

class BatchService:
    def __init__(self, batch_repo: BatchRepository):
        """Инжектим репозиторий, чтобы сервис не зависел от конкретной БД"""
        self.batch_repo = batch_repo

    @cached(ttl=60, key_prefix="batches_list")
    async def get_batches_list(self, is_closed: bool | None = None, offset: int = 0, limit: int = 20):
        """
        Получение списка партий.
        Декоратор автоматически закеширует результат.
        Если данные есть в Redis, до вызова репозитория дело даже не дойдет.
        """
        return await self.batch_repo.get_all(is_closed=is_closed, offset=offset, limit=limit)

    @cached(ttl=600, key_prefix="batch_detail")
    async def get_batch_with_products(self, batch_id: int):
        """
        Получение деталей партии с продукцией.
        """
        batch = await self.batch_repo.get_by_id_with_products(batch_id)
        return batch

    async def create_batch(self, data: BatchCreate):
        """
        Создание партии и инвалидация устаревшего кэша.
        """
        batch = await self.batch_repo.create(data)

        # Инвалидация по ТЗ
        await CacheService.delete("dashboard_stats")
        await CacheService.delete_pattern("batches_list:*")

        return batch

    async def update_batch(self, batch_id: int, data: BatchUpdate):
        """
        Обновление партии и полная инвалидация связанных данных.
        """
        batch = await self.batch_repo.update(batch_id, data)

        if batch:
            # Инвалидация по ТЗ
            await CacheService.delete(f"batch_detail:{batch_id}")
            await CacheService.delete(f"batch_statistics:{batch_id}")
            await CacheService.delete("dashboard_stats")
            await CacheService.delete_pattern("batches_list:*")

        return batch