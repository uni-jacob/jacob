import logging

from tortoise.transactions import in_transaction

from jacob.database import models


async def get_classrooms(university_id: int) -> list[models.Classroom]:
    """
    Получает список всех аудиторий в университете.

    Args:
        university_id: ИД университета

    Returns:
        list[University]: Список университетов.
    """
    async with in_transaction():
        all_ = await models.Classroom.filter(university_id=university_id)
        logging.info(f"Зарегистрированные аудитории: {all_}")
        return all_
