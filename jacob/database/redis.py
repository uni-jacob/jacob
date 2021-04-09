import os
from contextlib import AbstractAsyncContextManager

import aioredis


class RedisConn(AbstractAsyncContextManager):
    async def __aenter__(self):
        self.redis = await aioredis.create_redis_pool(
            os.getenv("REDIS_URL"),
            password=os.getenv("REDIS_PASSWORD"),
        )
        return self.redis

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.redis.close()
        await self.redis.wait_closed()


async def hmset(key: str, **kwargs):
    """Подключается к redis и обновляет значения ключа по словарю.

    Args:
        key: Ключ в redis
        **kwargs: Поля для обновления
    """
    async with RedisConn() as redis:
        await redis.hmset_dict(
            key,
            **kwargs,
        )


async def hget(key: str, field: str) -> str:
    """Подключается к Redis и получает поле словаря (хеша) по ключу

    Args:
        key: ключ
        field: поле

    Returns:
        str: значение
    """
    async with RedisConn() as redis:
        request = await redis.hget(
            key,
            field,
            encoding="utf-8",
        )

    return request
