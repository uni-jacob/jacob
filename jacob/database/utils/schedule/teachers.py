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
        return await models.Teacher.filter(university_id=university_id).order_by(
            "last_name"
        )


async def create_new_teacher(
    university_id: int,
    last_name: str,
    first_name: str,
    patronymic: str,
) -> models.Teacher:
    """
    Создаёт нового преподавателя.

    Args:
        university_id: ИД университета
        last_name: Фамилия преподавателя
        first_name: Имя преподавателя
        patronymic: Отчество преподавателя

    Returns:
        Teacher: Объект преподавателя
    """
    async with in_transaction():
        return await models.Teacher.create(
            university_id=university_id,
            last_name=last_name,
            first_name=first_name,
            patronymic=patronymic,
        )
