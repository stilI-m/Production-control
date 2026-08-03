from src.core.cache import CacheService
from src.data.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    async def aggregate_product(self, batch_id: int, code: str):
        """
        Логика агрегации продукции и инвалидации кэша.
        """
        product = await self.product_repo.aggregate(batch_id, code)

        # Если продукт успешно найден и обновлен
        if product:
            # Инвалидация по ТЗ:
            await CacheService.delete(f"batch_detail:{batch_id}")
            await CacheService.delete(f"batch_statistics:{batch_id}")
            await CacheService.delete("dashboard_stats")

        return product