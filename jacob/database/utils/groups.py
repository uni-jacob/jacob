import logging
from typing import Optional

from tortoise.transactions import in_transaction

from jacob.database import models
from jacob.database.utils.users import get_user_id


async def create_group(
    group_number: str,
    specialty: str,
    university_id: int,
) -> models.Group:
    """
    Создаёт новую группу

    Args:
        group_number: Номер группы
        specialty: Название специальности
        university_id: ИД университета

    Returns:
        Group: Объект созданной группы
    """
    async with in_transaction():
        logging.info(f"Создание группы с параметрами {locals()}")
        return await models.Group.create(**locals())


async def get_group(**kwargs) -> Optional[models.Group]:
    """Ищет одну группу в базе данных.

    Args:
        **kwargs: Параметры поиска

    Returns:
        Optional[Group]: Объект группы
    """
    async with in_transaction():
        return await models.Group.get_or_none(**kwargs)


async def update_group(group_id: int, **kwargs):
    """Обновляет группу в базе данных.

    Args:
        group_id: ИД группы
        **kwargs: Новые значения полей

    """
    async with in_transaction():
        await models.Group.filter(id=group_id).update(**kwargs)


async def get_managed_groups(vk_id: int) -> list[models.Admin]:
    """
    Получает список групп, которыми может управлять пользователь.

    Args:
        vk_id: ИД ВК пользователя.

    Returns:
        list[models.Group]: список модерируемых групп
    """
    user_id = await get_user_id(vk_id)
    async with in_transaction():
        query = await models.Admin.filter(user=user_id).prefetch_related(
            "group", "group__university"
        )
        logging.info(f"Найдены управляемые группы {query}")
        return query
