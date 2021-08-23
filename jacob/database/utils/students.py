from tortoise.transactions import in_transaction

from jacob.database import models


async def is_student(vk_id: int) -> bool:
    """Проверяет регистрацию студента.

    Args:
        vk_id: ИД ВК проверяемого пользователя

    Returns:
        bool: Зарегистрирован ли студент.
    """
    async with in_transaction():
        return bool(await models.Student.get_or_none(vk_id=vk_id))
