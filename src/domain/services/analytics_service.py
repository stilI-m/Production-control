from datetime import datetime, timezone
from src.core.cache import cached
from src.data.repositories.batch_repository import BatchRepository

class AnalyticsService:
    def __init__(self, batch_repo: BatchRepository):
        self.repo = batch_repo

    @cached(ttl=300, key_prefix="dashboard_stats")
    async def get_dashboard_statistics(self) -> dict:
        """
        Глобальная статистика. TTL: 5 минут.
        """
        stats = await self.repo.get_dashboard_stats()

        # Бизнес-логика: расчет прогресса в процентах
        total = stats["total_products"]
        agg = stats["aggregated_products"]

        rate = round((agg / total * 100), 2) if total > 0 else 0.0

        stats["aggregation_rate"] = rate
        # Метка времени, чтобы фронтенд знал, насколько свежие данные
        stats["cached_at"] = datetime.now(timezone.utc).isoformat()

        return stats

    @cached(ttl=300, key_prefix="batch_statistics")
    async def get_batch_statistics(self, batch_id: int) -> dict:
        """
        Статистика по одной партии. TTL: 5 минут.
        """
        stats = await self.repo.get_batch_stats(batch_id)

        # Бизнес-логика: расчет прогресса
        total = stats["total_products"]
        agg = stats["aggregated"]

        rate = round((agg / total * 100), 2) if total > 0 else 0.0
        stats["rate"] = rate

        return stats