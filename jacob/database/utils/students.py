import logging
from typing import Optional

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
        query = bool(await models.Student.get_or_none(user_id=user_id))
        logging.info(f"Пользователь {vk_id} {'' if query else 'не'} является студентом")
        return query


async def get_student(**kwargs) -> Optional[models.Student]:
    """Ищет одного студента в базе данных.

    Args:
        **kwargs: Параметры поиска

    Returns:
        Optional[Student]: Объект студента
    """
    async with in_transaction():
        return await models.Student.get_or_none(**kwargs)


async def create_student(
    user_id: int,
    first_name: str,
    last_name: str,
    group_id: int,
) -> models.Student:
    """
    Создаёт студента

    Args:
        user_id: ИД пользователя
        first_name: Имя
        last_name: Фамилия
        group_id: ИД группы

    Returns:
        Student: ИД студента
    """
    async with in_transaction():
        logging.info(f"Создание студента с параметрами {locals()}")
        return await models.Student.create(**locals())
