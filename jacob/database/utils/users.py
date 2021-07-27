from tortoise.transactions import in_transaction

from jacob.database import models


async def is_user(vk_id: int) -> bool:
    """Проверяет регистрацию анонимного пользователя.

    Args:
        vk_id: ИД ВК проверяемого пользователя

    Returns:
        bool: Зарегистрирован ли пользователь.
    """
    async with in_transaction():
        return bool(await models.User.get_or_none(vk_id=vk_id))
