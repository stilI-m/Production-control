from fastapi import HTTPException, status

from src.core.cache import cached, CacheService
from src.core.exceptions import ValidationError
from src.data.repositories.batch_repository import BatchRepository
from src.api.v1.schemas.batch import BatchCreate, BatchUpdate
from sqlalchemy.exc import IntegrityError
import logging

from src.domain.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)
class BatchService:
    def __init__(self, batch_repo: BatchRepository, webhook_service: WebhookService):
        """Инжектим репозиторий, чтобы сервис не зависел от конкретной БД"""
        self.batch_repo = batch_repo
        self.webhook_service = webhook_service

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
        try:
            batch = await self.batch_repo.create(data)
            logger.info("Успешно создана партия ID: %s", batch.id)
            try:
                await self.webhook_service.trigger_event(
                    event_type="batch_created",
                    payload={
                        "batch_id": batch.id,
                        "batch_number": batch.batch_number,
                        "status": "created"
                    }
                )
            except Exception as e:
                # Логируем ошибку, но не даем ей сломать создание партии
                logger.error("Ошибка при отправке вебхука batch_created: %s", e)
            return batch
        except IntegrityError:
            logger.exception("Ошибка внешнего ключа при создании партии")
            # Выдаем стандартную ошибку FastAPI
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Указан несуществующий work_center_id"
            )
        except Exception as e:
            logger.exception("Непредвиденная ошибка при создании партии")
            raise e

    async def update_batch(self, batch_id: int, data: BatchUpdate):
        """
        Обновление партии и полная инвалидация связанных данных.
        """
        # 1. Пытаемся обновить в БД и ловим ошибки ForeignKey / Unique
        try:
            batch = await self.batch_repo.update(batch_id, data)
        except IntegrityError:
            # logger.exception автоматически добавит Traceback в лог-файл
            logger.exception("Ошибка целостности БД при обновлении партии ID: %s", batch_id)
            raise ValidationError("Указан несуществующий WorkCenter или Product")
        except Exception as e:
            logger.exception("Непредвиденная ошибка при обновлении партии ID: %s", batch_id)
            raise e

        # 2. Если все прошло успешно
        if batch:
            logger.info("Партия ID: %s успешно обновлена", batch_id)

            # Инвалидация по ТЗ
            await CacheService.delete(f"batch_detail:{batch_id}")
            await CacheService.delete(f"batch_statistics:{batch_id}")
            await CacheService.delete("dashboard_stats")
            await CacheService.delete_pattern("batches_list:*")

            logger.info("Кэш для партии ID: %s успешно инвалидирован", batch_id)
        else:
            # Если репозиторий вернул None (партии с таким ID нет)
            logger.warning("Попытка обновить несуществующую партию ID: %s", batch_id)

        return batch