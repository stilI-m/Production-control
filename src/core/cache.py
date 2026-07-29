import json
import os
from functools import wraps
from typing import Any, Callable

from redis.asyncio import Redis

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

class CacheService:

    @staticmethod
    async def delete(key: str) -> None:
        await redis_client.delete(key)
    @staticmethod
    async def delete_pattern(pattern:str) -> None:
        cursor = '0'
        while cursor != 0:
            cursor, keys = await redis_client.scan(cursor=cursor, match=pattern)
            if keys:
                await redis_client.delete(*keys)

def cached(ttl: int, key_prefix: str) -> Callable:
    """
    Декоратор для кэширования результатов асинхронных функций.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 1. Формируем уникальный ключ на основе аргументов
            key_parts = [key_prefix]

            # Добавляем позиционные аргументы (игнорируя self/cls, если это метод класса)
            if args:
                key_parts.extend([str(a) for a in args if not hasattr(a, '__dict__')])

            # Добавляем именованные аргументы, отсортированные по ключу для стабильности
            if kwargs:
                key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])

            cache_key = ":".join(key_parts)

            # 2. Проверяем наличие в кэше
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                # Если нашли — десериализуем и возвращаем
                return json.loads(cached_data)

            # 3. Если кэша нет, выполняем функцию
            result = await func(*args, **kwargs)

            # 4. Записываем результат в кэш
            if result is not None:
                # Проверяем, есть ли у результата метод model_dump (Pydantic v2)
                if hasattr(result, "model_dump"):
                    data_to_cache = result.model_dump(mode="json")
                # Для списков Pydantic моделей
                elif isinstance(result, list) and len(result) > 0 and hasattr(result[0], "model_dump"):
                    data_to_cache = [item.model_dump(mode="json") for item in result]
                else:
                    data_to_cache = result

                # Сериализуем в JSON. default=str спасает при наличии datetime или UUID
                json_data = json.dumps(data_to_cache, default=str)
                await redis_client.set(cache_key, json_data, ex=ttl)

            return result
        return wrapper
    return decorator
