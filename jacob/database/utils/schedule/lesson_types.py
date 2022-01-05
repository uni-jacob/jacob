from tortoise.transactions import in_transaction

from jacob.database import models


async def get_lesson_types() -> list[models.LessonType]:
    """
    Получает список доступных типов пар.

    Returns:
        list[LessonType]: список типов пар
    """
    async with in_transaction():
        return await models.LessonType.all()
