import logging

from tortoise.transactions import in_transaction

from jacob.database import models
from jacob.services.exceptions import UniversityNotFound


async def get_universities() -> list[models.University]:
    """
    Получает список всех университетов.

    Returns:
        list[University]: Список университетов.
    """
    async with in_transaction():
        all_ = await models.University.all()
        logging.info(f"Зарегистрированные университеты: {all_}")
        return all_


async def get_university_by_id(university_id: int) -> models.University:
    """
    Получает университет по его ИД.

    Args:
        university_id: ИД университета.

    Raises:
        UniversityNotFound: если университет не существует

    Returns:
        University: Объект университета.
    """
    async with in_transaction():
        query = await models.University.get_or_none(id=university_id)

        if query is None:
            raise UniversityNotFound(f"Университет №{university_id} не найден")

        return query


async def create_new_university(name: str) -> models.University:
    """
    Создаёт новый университет.

    Args:
        name: Название университета

    Returns:
        University: Объект созданного университета
    """
    async with in_transaction():
        logging.info(f"Создание университета с параметрами {locals()}")
        return await models.University.create(**locals())


async def update_university_abbreviation(university_id: int, new_abbreviation: str):
    """
    Изменяет аббревиатуру университета.

    Args:
        university_id: Идентификатор университета
        new_abbreviation: Новая аббревиатура
    """
    async with in_transaction():
        logging.info(
            f"Обновление аббревиатуры университета №{university_id}. Новое значение {new_abbreviation}",
        )
        await models.University.filter(id=university_id).update(
            abbreviation=new_abbreviation,
        )
