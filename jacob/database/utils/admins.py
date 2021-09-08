from tortoise.transactions import in_transaction

from jacob.database import models


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
