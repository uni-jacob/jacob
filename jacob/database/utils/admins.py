import logging

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
        query = bool(await models.Admin.filter(user_id=user_id))
        logging.info(f"{user_id} {'' if query else 'не'} админ")
        return query


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
        logging.info(f"Создание админа с параметрами {locals()}")
        return await models.Admin.create(**locals())
