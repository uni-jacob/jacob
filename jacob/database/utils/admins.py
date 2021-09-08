from tortoise.transactions import in_transaction

from jacob.database import models


async def is_admin(user_id: int) -> bool:
    """
    Проверяет, является ли пользователь админом

    Args:
        user_id: ИД пользователя

    Returns:
        bool: Пользователь админ?
    """
    async with in_transaction():
        return bool(await models.Admin.get_or_none(user_id=user_id))


async def create_admin(user_id: int, group_id: int) -> models.Admin:
    """
    Создаёт нового администратора
    Args:
        user_id: ИД пользователя
        group_id: ИД группы

    Returns:
        Admin: Объект администратора
    """
    async with in_transaction():
        return await models.Admin.create(**locals())
