from tortoise.transactions import in_transaction

from jacob.database import models


async def get_teachers(university_id: int) -> list[models.Teacher]:
    """
    Получает список преподавателей в университете.

    Args:
        university_id: ИД университета.

    Returns:
        list[Teacher]: Список преподавателей
    """
    async with in_transaction():
        return await models.Teacher.filter(university_id=university_id)
