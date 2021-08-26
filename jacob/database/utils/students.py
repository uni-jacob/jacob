from tortoise.transactions import in_transaction

from jacob.database import models
from jacob.database.utils.users import get_user_id


async def is_student(vk_id: int) -> bool:
    """Проверяет регистрацию студента.

    Args:
        vk_id: ИД ВК проверяемого пользователя

    Returns:
        bool: Зарегистрирован ли студент.
    """
    user_id = await get_user_id(vk_id)
    async with in_transaction():
        return bool(await models.Student.get_or_none(user_id=user_id))
