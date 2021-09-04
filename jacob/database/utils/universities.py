import logging

from tortoise.transactions import in_transaction

from jacob.database import models


async def get_universities() -> list[models.University]:
    """
    Получает список всех университетов.

    Returns:
        list[University]: Список университетов.
    """
    async with in_transaction():
        return await models.University.all()


async def get_university_by_id(university_id: int) -> models.University:
    """
    Получает университет по его ИД.
    Args:
        university_id: ИД университета.

    Returns:
        University: Объект университета.
    """
    async with in_transaction():
        return await models.University.get_or_none(id=university_id)


async def create_new_university(university_name: str) -> models.University:
    """
    Создаёт новый университет.

    Args:
        university_name: Название университета

    Returns:
        University: Объект созданного университета
    """
    async with in_transaction():
        return await models.University.create(name=university_name)


async def update_university_abbreviation(university_id: int, new_abbreviation: str):
    """
    Изменяет аббревиатуру университета.

    Args:
        university_id: Идентификатор университета
        new_abbreviation: Новая аббревиатура
    """
    async with in_transaction():
        logging.debug(university_id)
        logging.debug(new_abbreviation)
        await models.University.filter(id=university_id).update(
            abbreviation=new_abbreviation
        )
