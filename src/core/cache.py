import json
import os
from functools import wraps
from typing import Any, Callable

from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)
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
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            key_parts = [key_prefix]
            if args:
                key_parts.extend([str(a) for a in args if not hasattr(a, '__dict__')])
            if kwargs:
                key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])

            cache_key = ":".join(key_parts)

            # 1. Безопасное чтение из Redis
            try:
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                # Если Redis недоступен, просто логируем и идем дальше (к выполнению функции)
                logger.warning("Ошибка чтения из кэша Redis для ключа %s: %s", cache_key, e)

            # 2. Выполняем саму функцию
            result = await func(*args, **kwargs)

            # 3. Безопасная запись в Redis
            if result is not None:
                if hasattr(result, "model_dump"):
                    data_to_cache = result.model_dump(mode="json")
                elif isinstance(result, list) and len(result) > 0 and hasattr(result[0], "model_dump"):
                    data_to_cache = [item.model_dump(mode="json") for item in result]
                else:
                    data_to_cache = result

                json_data = json.dumps(data_to_cache, default=str)

                try:
                    await redis_client.set(cache_key, json_data, ex=ttl)
                except Exception as e:
                    logger.warning("Ошибка записи в кэш Redis для ключа %s: %s", cache_key, e)

            return result
        return wrapper
    return decorator
