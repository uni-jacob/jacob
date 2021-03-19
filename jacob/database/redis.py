import os

import aioredis


async def hmset(key: str, **kwargs):
    """Подключается к redis и обновляет значения ключа по словарю.

    Args:
        key: Ключ в redis

    """
    redis = await aioredis.create_redis_pool(os.getenv("REDIS_URL"))
    await redis.hmset_dict(
        key,
        **kwargs,
    )
    redis.close()
    await redis.wait_closed()


async def hget(key: str, field: str):
    redis = await aioredis.create_redis_pool(os.getenv("REDIS_URL"))
    request = await redis.hget(
        key,
        field,
        encoding="utf-8",
    )
    redis.close()
    await redis.wait_closed()

    return request
