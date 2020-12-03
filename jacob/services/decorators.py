import functools

from loguru import logger
from vkwave import bots


@functools.wraps
def context_logger(func: callable):
    """Декоратор для расширения записей в логах.

    Args:
        func: Функция для декорирования

    Returns:
        decorator: Декорированная функция
    """

    def decorator(ans: bots.SimpleBotEvent):
        with logger.contextualize(user_id=ans.object.object.message.from_id):
            return func(ans)

    return decorator
