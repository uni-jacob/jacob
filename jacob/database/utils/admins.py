import logging
from typing import Optional

from tortoise.transactions import in_transaction

from jacob.database import models
from jacob.services.exceptions import GroupNotFound


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


async def get_admin(**kwargs) -> Optional[models.Admin]:
    """Ищет одного админа в базе данных.

    Args:
        **kwargs: Параметры поиска

    Returns:
        Optional[Admin]: Объект админа
    """
    async with in_transaction():
        return await models.Admin.get_or_none(**kwargs)


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


async def update_group_selection(user_id: int, group_id: int, is_active: bool):
    """Изменяет статус активности группы у админа.

    Args:
        user_id: ИД пользователя
        group_id: ИД группы
        is_active: Активность группы

    """
    async with in_transaction():
        await models.Admin.filter(user_id=user_id, group_id=group_id).update(
            is_active=is_active,
        )


async def toggle_group_selection(group_id: int, user_id: int):
    """
    Переключает активность группы.

    Args:
        group_id: ИД группы
        user_id: ИД пользователя

    Raises:
        GroupNotFound: когда невозможно найти группу

    Returns:
        bool: Новое состояние группы
    """
    async with in_transaction():
        group = await get_admin(group_id=group_id)
        selection = not group.is_active
        try:
            logging.info(
                f"Переключение активности группы {group_id} в положение {selection}",
            )
        except AttributeError:
            raise GroupNotFound(f"Группа №{group_id} не существует")

        await update_group_selection(user_id, group_id, selection)
        return selection
